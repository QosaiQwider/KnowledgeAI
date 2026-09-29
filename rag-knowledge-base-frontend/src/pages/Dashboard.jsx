import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
    BookOpen,
    FileText,
    MessageSquare,
    Plus
} from 'lucide-react';

import { api } from '../services/api';


export default function Dashboard() {

    const [kbs, setKbs] = useState([]);
    const [error, setError] = useState('');


    // =====================================================
    // LOAD KNOWLEDGE BASES
    // =====================================================

    useEffect(() => {

        api
            .knowledgeBases()
            .then(setKbs)
            .catch(e => setError(e.message));

    }, []);


    // =====================================================
    // TOTAL DOCUMENTS
    // =====================================================

    const docs = kbs.reduce(
        (total, kb) =>
            total + (
                kb.document_count ||
                kb.documents?.length ||
                0
            ),
        0
    );


    // =====================================================
    // TOTAL CONVERSATIONS
    // =====================================================

    const conversations = kbs.reduce(
        (total, kb) =>
            total + (
                kb.conversation_count ||
                0
            ),
        0
    );


    return (
        <>

            {/* =============================================
                PAGE HEADER
            ============================================== */}

            <div className="page-head">

                <div>
                    <h1>Dashboard</h1>

                    <p>
                        Your document knowledge workspace.
                    </p>
                </div>


                <Link
                    className="primary linkbtn"
                    to="/knowledge-bases"
                >
                    + New knowledge base
                </Link>

            </div>


            {/* =============================================
                ERROR
            ============================================== */}

            {error && (
                <div className="error">
                    {error}
                </div>
            )}


            {/* =============================================
                STATISTICS
            ============================================== */}

            <div className="stats">

                <div className="stat">

                    <BookOpen />

                    <b>
                        {kbs.length}
                    </b>

                    <span>
                        Knowledge bases
                    </span>

                </div>


                <div className="stat">

                    <FileText />

                    <b>
                        {docs}
                    </b>

                    <span>
                        Documents
                    </span>

                </div>


                <div className="stat">

                    <MessageSquare />

                    <b>
                        {conversations}
                    </b>

                    <span>
                        Conversations
                    </span>

                </div>

            </div>


            {/* =============================================
                RECENT KNOWLEDGE BASES
            ============================================== */}

            <section>

                <h2>
                    Recent knowledge bases
                </h2>


                <div className="cards">

                    {kbs
                        .slice(0, 6)
                        .map(kb => (

                            <Link
                                className="kb-card"

                                // IMPORTANT:
                                // Backend returns "id"
                                key={kb.id}

                                to={`/knowledge-bases/${kb.id}`}
                            >

                                <BookOpen />

                                <div>

                                    <h3>
                                        {kb.name}
                                    </h3>

                                    <p>
                                        {kb.document_count || 0}
                                        {' '}
                                        documents
                                    </p>

                                </div>

                            </Link>

                        ))}


                    {!kbs.length && !error && (

                        <div className="empty">

                            <Plus />

                            <p>
                                Create your first knowledge base.
                            </p>

                        </div>

                    )}

                </div>

            </section>

        </>
    );
}