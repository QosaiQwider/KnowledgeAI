const BASE =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000';


async function request(path, options = {}) {

  const token = localStorage.getItem('token');

  const headers = {
    ...(options.body instanceof FormData
      ? {}
      : { 'Content-Type': 'application/json' }),
    ...options.headers
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(
    `${BASE}${path}`,
    {
      ...options,
      headers
    }
  );


  // ==========================================
  // ERROR HANDLING
  // ==========================================

  if (!res.ok) {

    let msg = 'Request failed';

    try {

      const data = await res.json();

      msg =
        data.detail ||
        data.message ||
        msg;

    } catch {
      // Keep default error
    }

    throw new Error(msg);
  }


  // ==========================================
  // NO CONTENT
  // ==========================================

  if (res.status === 204) {
    return null;
  }


  // ==========================================
  // JSON RESPONSE
  // ==========================================

  return res.json();
}


export const api = {

  // ======================================================
  // AUTH
  // ======================================================

  register: data =>
    request(
      '/register',
      {
        method: 'POST',
        body: JSON.stringify(data)
      }
    ),


  login: data =>
    request(
      '/login',
      {
        method: 'POST',
        body: JSON.stringify(data)
      }
    ),


  // ======================================================
  // KNOWLEDGE BASES
  // ======================================================

  knowledgeBases: () =>
    request('/knowledge-bases/'),


  knowledgeBase: id =>
    request(`/knowledge-bases/${id}`),


  createKnowledgeBase: data =>
    request(
      '/knowledge-bases/',
      {
        method: 'POST',
        body: JSON.stringify(data)
      }
    ),


  deleteKnowledgeBase: id =>
    request(
      `/knowledge-bases/${id}`,
      {
        method: 'DELETE'
      }
    ),


  // ======================================================
  // DOCUMENTS
  // ======================================================

  documents: kbId =>
    request(
      `/knowledge-bases/${kbId}/documents`
    ),


  uploadDocuments: (kbId, files) => {

    const formData = new FormData();

    [...files].forEach(file => {
      formData.append(
        'files',
        file
      );
    });

    return request(
      `/knowledge-bases/${kbId}/documents`,
      {
        method: 'POST',
        body: formData
      }
    );
  },


  deleteDocument: id =>
    request(
      `/documents/${id}`,
      {
        method: 'DELETE'
      }
    ),


  // ======================================================
  // CONVERSATIONS
  // ======================================================

  conversations: kbId =>
    request(
      `/knowledge-bases/${kbId}/conversations`
    ),


  createConversation: kbId =>
    request(
      `/knowledge-bases/${kbId}/conversations`,
      {
        method: 'POST'
      }
    ),


  deleteConversation: id =>
    request(
      `/conversations/${id}`,
      {
        method: 'DELETE'
      }
    ),


  // ======================================================
  // MESSAGES
  // ======================================================

  messages: conversationId =>
    request(
      `/conversations/${conversationId}/messages`
    ),


  sendMessage: (conversationId, message) =>
    request(
      `/conversations/${conversationId}/messages`,
      {
        method: 'POST',

        // IMPORTANT:
        // Backend MessageRequest expects "content"
        body: JSON.stringify({
          content: message
        })
      }
    )

};