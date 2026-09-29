import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
    FileText,
    MessageSquare,
    Trash2,
    Upload
} from 'lucide-react';

import { api } from '../services/api';
import StatusBadge from '../components/StatusBadge';


export default function KnowledgeBaseDetail() {

    const { id } = useParams();
    const nav = useNavigate();
    const input = useRef();

    const [docs, setDocs] = useState([]);
    const [convs, setConvs] = useState([]);
    const [error, setError] = useState('');
    const [uploading, setUploading] = useState(false);


    // =====================================================
    // LOAD DATA
    // =====================================================

    const load = async () => {

        try {

            const documents = await api.documents(id);

            console.log("DOCUMENTS:", documents);

            setDocs(documents);

        } catch (e) {

            console.error("DOCUMENT LOAD ERROR:", e);

            setError(e.message);
        }


        try {

            const conversations = await api.conversations(id);

            setConvs(conversations);

        } catch (e) {

            // Conversations endpoint may not exist yet
            setConvs([]);
        }
    };


    useEffect(() => {

        load();

    }, [id]);


    // =====================================================
    // UPLOAD
    // =====================================================

    async function upload(e) {

        const files = e.target.files;

        if (!files?.length) {
            return;
        }

        setUploading(true);
        setError('');

        try {

            await api.uploadDocuments(
                id,
                files
            );

            await load();

        } catch (e) {

            console.error(
                "UPLOAD ERROR:",
                e
            );

            setError(
                e.message
            );

        } finally {

            setUploading(false);

            e.target.value = '';
        }
    }


    // =====================================================
    // DELETE DOCUMENT
    // =====================================================

    async function del(docId) {

        console.log(
            "DELETE BUTTON CLICKED"
        );

        console.log(
            "DOCUMENT ID:",
            docId
        );


        if (!docId) {

            console.error(
                "Document ID is missing!"
            );

            setError(
                "Document ID is missing"
            );

            return;
        }


        const confirmed = window.confirm(
            "Delete this document and indexed data?"
        );


        if (!confirmed) {

            console.log(
                "DELETE CANCELLED"
            );

            return;
        }


        try {

            setError('');


            console.log(
                "SENDING DELETE REQUEST:",
                docId
            );


            const response =
                await api.deleteDocument(
                    docId
                );


            console.log(
                "DELETE RESPONSE:",
                response
            );


            // Remove immediately from UI
            setDocs(currentDocs =>
                currentDocs.filter(
                    document =>
                        document.id !== docId
                )
            );


            // Reload from backend
            await load();


        } catch (e) {

            console.error(
                "DELETE ERROR:",
                e
            );


            setError(
                e.message ||
                "Failed to delete document"
            );
        }
    }


    // =====================================================
    // OPEN CHAT
    // =====================================================

    async function openChat() {

        try {

            const c =
                await api.createConversation(
                    id
                );


            nav(
                `/chat/${c.id}`,
                {
                    state: {
                        kbId: id
                    }
                }
            );

        } catch (e) {

            setError(
                e.message
            );
        }
    }


    // =====================================================
    // UI
    // =====================================================

    return (
        <>

            <div className="page-head">

                <div>

                    <h1>
                        Knowledge Base #{id}
                    </h1>

                    <p>
                        Upload PDF, DOCX, PPTX or TXT files
                        and chat only with this knowledge base.
                    </p>

                </div>


                <button
                    type="button"
                    className="primary"
                    onClick={openChat}
                >

                    <MessageSquare size={17} />

                    Open new chat

                </button>

            </div>


            {error && (

                <div className="error">
                    {error}
                </div>

            )}


            {/* ========================================= */}
            {/* DOCUMENTS */}
            {/* ========================================= */}

            <section className="panel">

                <div className="section-head">

                    <div>

                        <h2>
                            Documents
                        </h2>

                        <p>
                            Processing status is updated
                            by the backend.
                        </p>

                    </div>


                    <div>

                        <input
                            ref={input}
                            hidden
                            multiple
                            type="file"
                            accept=".pdf,.docx,.pptx,.txt"
                            onChange={upload}
                        />


                        <button
                            type="button"
                            className="secondary"
                            disabled={uploading}
                            onClick={() =>
                                input.current?.click()
                            }
                        >

                            <Upload size={17} />

                            {
                                uploading
                                    ? 'Uploading...'
                                    : 'Upload files'
                            }

                        </button>

                    </div>

                </div>


                <div className="table-wrap">

                    <table>

                        <thead>

                            <tr>

                                <th>File</th>
                                <th>Type</th>
                                <th>Size</th>
                                <th>Status</th>
                                <th></th>

                            </tr>

                        </thead>


                        <tbody>

                            {docs.map(d => (

                                <tr key={d.id}>

                                    <td>

                                        <FileText size={16} />

                                        {d.file_name}

                                    </td>


                                    <td>

                                        {d.file_type || '—'}

                                    </td>


                                    <td>

                                        {
                                            d.file_size
                                                ? `${Math.round(
                                                    d.file_size / 1024
                                                )} KB`
                                                : '—'
                                        }

                                    </td>


                                    <td>

                                        <StatusBadge
                                            status={d.status}
                                        />

                                    </td>


                                    <td>

                                        <button
                                            type="button"
                                            className="icon danger"
                                            title="Delete document"
                                            onClick={() =>
                                                del(d.id)
                                            }
                                        >

                                            <Trash2 size={17} />

                                        </button>

                                    </td>

                                </tr>

                            ))}


                            {!docs.length && (

                                <tr>

                                    <td
                                        colSpan="5"
                                        className="muted"
                                    >

                                        No documents uploaded yet.

                                    </td>

                                </tr>

                            )}

                        </tbody>

                    </table>

                </div>

            </section>


            {/* ========================================= */}
            {/* CONVERSATIONS */}
            {/* ========================================= */}

            <section className="panel">

                <div className="section-head">

                    <div>

                        <h2>
                            Conversation history
                        </h2>

                        <p>
                            Continue a previous conversation.
                        </p>

                    </div>

                </div>


                <div className="conversation-list">

                    {convs.map(c => (

                        <button
                            type="button"
                            key={c.id}
                            onClick={() =>
                                nav(
                                    `/chat/${c.id}`,
                                    {
                                        state: {
                                            kbId: id
                                        }
                                    }
                                )
                            }
                        >

                            <MessageSquare size={17} />

                            <span>

                                {
                                    c.title ||
                                    `Conversation #${c.id}`
                                }

                            </span>

                        </button>

                    ))}


                    {!convs.length && (

                        <p className="muted">
                            No conversations yet.
                        </p>

                    )}

                </div>

            </section>

        </>
    );
}