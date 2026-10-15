
import {
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from 'react'
import './App.css'

interface DocumentRecord {
  document_id: string
  filename: string
  extracted_units: number
  chunks_created: number
  model_name: string
  created_at: string
}

interface ClaimVerification {
  claim: string
  status: string
  evidence_ids: string[]
  explanation: string
}

interface EvidenceItem {
  evidence_id: string
  source_name: string
  page_number: number | null
  section_number: number | null
  relevance_score: number
  text: string
}

interface AnswerResponse {
  document_id: string
  question: string
  answer: string
  citations_valid: boolean
  cited_evidence_ids: string[]
  invalid_citation_ids: string[]
  missing_citation: boolean
  claim_verifications: ClaimVerification[]
  evidence: EvidenceItem[]
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const evidenceNodes = [
  { id: '01', label: 'SOURCE DOC', x: 18, y: 29, kind: 'source' },
  { id: '02', label: 'RETRIEVAL', x: 78, y: 23, kind: 'retrieval' },
  { id: '03', label: 'PASSAGE 04', x: 84, y: 66, kind: 'passage' },
  { id: '04', label: 'CLAIM CHECK', x: 28, y: 79, kind: 'verify' },
  { id: '05', label: 'CITATION', x: 50, y: 12, kind: 'citation' },
]

const networkNodes = [
  [80, 120], [260, 240], [420, 130], [610, 290],
  [800, 180], [1010, 300], [1240, 160], [1380, 250],
  [180, 410], [360, 500], [720, 530], [1080, 520],
  [520, 680], [900, 730], [1290, 700], [80, 700],
  [260, 800], [610, 920], [1050, 930], [1380, 880],
  [1240, 990],
]

function App() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([])
  const [loadingDocuments, setLoadingDocuments] = useState(true)
  const [documentError, setDocumentError] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')

  const [question, setQuestion] = useState('')
  const [selectedDocumentId, setSelectedDocumentId] = useState('')
  const [answerResult, setAnswerResult] =
    useState<AnswerResponse | null>(null)
  const [answerLoading, setAnswerLoading] = useState(false)
  const [answerError, setAnswerError] = useState('')

  const loadDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/`)

      if (!response.ok) {
        throw new Error('Unable to load documents.')
      }

      const data = await response.json()
      const loadedDocuments: DocumentRecord[] = data.documents ?? []

      setDocuments(loadedDocuments)
      setDocumentError('')

      setSelectedDocumentId((currentId) => {
        if (
          currentId &&
          loadedDocuments.some(
            (document) => document.document_id === currentId,
          )
        ) {
          return currentId
        }

        return loadedDocuments[0]?.document_id ?? ''
      })
    } catch {
      setDocumentError(
        'Could not connect to the document service. Check the backend.',
      )
    } finally {
      setLoadingDocuments(false)
    }
  }

  useEffect(() => {
    void loadDocuments()
  }, [])

  const handleUpload = async (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const input = event.currentTarget
    const file = input.files?.[0]

    if (!file) return

    setUploading(true)
    setUploadMessage('Uploading and processing document...')
    setAnswerError('')
    setAnswerResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(
        `${API_BASE_URL}/api/documents/upload`,
        {
          method: 'POST',
          body: formData,
        },
      )

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Document upload failed.',
        )
      }

      setUploadMessage(
        'Upload successful. Refreshing your document library...',
      )

      await loadDocuments()

      setUploadMessage(
        'Document uploaded successfully. Check your library.',
      )
    } catch (error) {
      setUploadMessage(
        error instanceof Error
          ? error.message
          : 'An unexpected upload error occurred.',
      )
    } finally {
      setUploading(false)
      input.value = ''
    }
  }

  const handleQuestionSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    if (!question.trim()) {
      setAnswerError('Please enter a question.')
      setAnswerResult(null)
      return
    }

    if (!selectedDocumentId) {
      setAnswerError('Upload or select a document first.')
      setAnswerResult(null)
      return
    }

    setAnswerLoading(true)
    setAnswerError('')
    setAnswerResult(null)

    try {
      const response = await fetch(`${API_BASE_URL}/api/answers/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: selectedDocumentId,
          question: question.trim(),
        }),
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Could not generate an answer.',
        )
      }

      setAnswerResult(data as AnswerResponse)
    } catch (error) {
      setAnswerError(
        error instanceof Error
          ? error.message
          : 'An unexpected error occurred.',
      )
    } finally {
      setAnswerLoading(false)
    }
  }

  return (
    <main className="research-app" id="top">
      <div className="neural-background" aria-hidden="true">
        <div className="neural-glow neural-glow-one" />
        <div className="neural-glow neural-glow-two" />
        <div className="neural-grid" />

        <svg
          className="ai-network"
          viewBox="0 0 1440 1100"
          preserveAspectRatio="xMidYMin slice"
        >
          <defs>
            <linearGradient id="aiConnection">
              <stop offset="0%" stopColor="#7CE8FF" stopOpacity="0" />
              <stop offset="50%" stopColor="#7CE8FF" stopOpacity=".85" />
              <stop offset="100%" stopColor="#B8FF65" stopOpacity="0" />
            </linearGradient>

            <radialGradient id="aiNodeGlow">
              <stop offset="0%" stopColor="#7CE8FF" stopOpacity=".8" />
              <stop offset="100%" stopColor="#7CE8FF" stopOpacity="0" />
            </radialGradient>
          </defs>

          <g className="network-connections">
            <path d="M80 120 L260 240 L420 130 L610 290 L800 180 L1010 300 L1240 160 L1380 250" />
            <path d="M80 120 L180 410 L420 130 L360 500 L610 290 L720 530 L1010 300 L1080 520 L1380 250" />
            <path d="M180 410 L360 500 L520 680 L720 530 L900 730 L1080 520 L1290 700" />
            <path d="M360 500 L260 800 L520 680 L610 920 L900 730 L1050 930 L1290 700 L1380 880" />
            <path d="M80 700 L260 800 L360 500 L720 530 L610 920 L900 730 L1240 990" />
            <path d="M800 180 L720 530 L900 730 L1010 300" />
            <path d="M1240 160 L1080 520 L1290 700 L1380 880" />
          </g>

          <g className="network-data-streams">
            <path d="M80 120 L260 240 L420 130 L610 290 L800 180 L1010 300" />
            <path d="M180 410 L360 500 L520 680 L720 530 L900 730 L1080 520" />
            <path d="M260 800 L520 680 L610 920 L900 730 L1050 930" />
          </g>

          <g className="network-nodes">
            {networkNodes.map(([cx, cy], index) => (
              <g
                key={`${cx}-${cy}`}
                className={`network-node network-node-${index % 4}`}
                style={{ animationDelay: `${index * -0.37}s` }}
              >
                <circle cx={cx} cy={cy} r="25" fill="url(#aiNodeGlow)" />
                <circle
                  className="network-node-core"
                  cx={cx}
                  cy={cy}
                  r={index % 5 === 0 ? 4 : 2.5}
                />
              </g>
            ))}
          </g>
        </svg>

        <div className="neural-particles">
          {Array.from({ length: 30 }, (_, index) => (
            <span
              key={index}
              className={`particle particle-${index % 6}`}
              style={{
                left: `${(index * 37 + 11) % 100}%`,
                top: `${(index * 53 + 7) % 100}%`,
                animationDelay: `${(index % 8) * -0.8}s`,
              }}
            />
          ))}
        </div>
      </div>

      <header className="research-header">
        <a
          className="research-brand"
          href="#top"
          aria-label="RAG Citation Agent home"
        >
          <span className="brand-mark">
            <span />
            <span />
            <span />
          </span>
          <span>
            RAG<span className="brand-slash">/</span>CA
          </span>
          <span className="brand-divider" />
          <span className="brand-caption">RESEARCH SYSTEM</span>
        </a>

        <nav className="research-nav" aria-label="Main navigation">
          <a className="active" href="#overview">Overview</a>
          <a href="#library">Library</a>
          <a href="#workspace">Ask AI</a>
        </nav>

        <div className="system-indicator">
          <span className="indicator-dot" />
          <span>LOCAL SYSTEM</span>
        </div>
      </header>

      <section className="research-hero" id="overview">
        <div className="hero-content">
          <div className="eyebrow">
            <span className="eyebrow-line" />
            RETRIEVAL-AUGMENTED INTELLIGENCE
          </div>

          <h1>
            Intelligence
            <br />
            needs <span>evidence.</span>
          </h1>

          <p className="hero-copy">
            Search your knowledge. Ask better questions.
            Trace every answer back to the document that supports it.
          </p>

          <div className="hero-actions">
            <a className="primary-action" href="#workspace">
              Start researching <span>↗</span>
            </a>
            <a className="secondary-action" href="#library">
              Explore your library <span>↓</span>
            </a>
          </div>

          <div className="hero-meta">
            <span>01 / DOCUMENT INTELLIGENCE</span>
            <span>BUILT FOR TRACEABLE ANSWERS</span>
          </div>
        </div>

        <div className="evidence-visual">
          <div className="visual-header">
            <span>LIVE EVIDENCE MAP</span>
            <span className="visual-coordinate">NODE NETWORK / 001</span>
          </div>

          <div className="evidence-map">
            <div className="map-ring ring-one" />
            <div className="map-ring ring-two" />
            <div className="map-ring ring-three" />
            <div className="map-crosshair crosshair-one" />
            <div className="map-crosshair crosshair-two" />

            <svg
              className="evidence-lines"
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <defs>
                <linearGradient id="evidenceGradient">
                  <stop offset="0%" stopColor="#B8FF65" stopOpacity=".2" />
                  <stop offset="50%" stopColor="#7CE8FF" stopOpacity=".9" />
                  <stop offset="100%" stopColor="#B8FF65" stopOpacity=".25" />
                </linearGradient>
              </defs>

              <path d="M18 29 L50 12 L78 23 L84 66 L28 79 Z" />
              <path d="M18 29 L84 66 M78 23 L28 79 M50 12 L28 79" />
              <path
                className="active-evidence-line"
                d="M18 29 L50 12 L78 23 L84 66 L28 79 Z"
              />
            </svg>

            {evidenceNodes.map((node) => (
              <div
                key={node.id}
                className={`evidence-node node-${node.kind}`}
                style={{ left: `${node.x}%`, top: `${node.y}%` }}
              >
                <span className="node-pulse" />
                <span className="node-core" />
                <span className="node-label">
                  <small>{node.id}</small>
                  {node.label}
                </span>
              </div>
            ))}

            <div className="map-center">
              <div className="center-rings">
                <span />
                <span />
                <span />
              </div>
              <span className="center-label">EVIDENCE</span>
              <span className="center-sub-label">CONNECTED</span>
            </div>

            <span className="map-readout readout-top">TRACE / ACTIVE</span>
            <span className="map-readout readout-bottom">SOURCE → CLAIM</span>
          </div>

          <div className="visual-footer">
            <span><i className="legend-lime" /> SOURCE</span>
            <span><i className="legend-cyan" /> RETRIEVAL</span>
            <span><i className="legend-outline" /> CITATION PATH</span>
          </div>
        </div>
      </section>

      <section className="capability-strip" aria-label="System capabilities">
        <div className="capability-intro">
          <span className="section-index">SYSTEM / 001</span>
          <span>FROM DOCUMENT TO PROOF</span>
        </div>

        <article className="capability">
          <span className="capability-number">01</span>
          <div>
            <h2>Retrieve</h2>
            <p>Find the passages that matter.</p>
          </div>
        </article>

        <article className="capability">
          <span className="capability-number">02</span>
          <div>
            <h2>Reason</h2>
            <p>Build answers from source context.</p>
          </div>
        </article>

        <article className="capability">
          <span className="capability-number">03</span>
          <div>
            <h2>Verify</h2>
            <p>Follow claims back to evidence.</p>
          </div>
        </article>
      </section>

      <section className="research-workspace" id="workspace">
        <div className="workspace-heading">
          <div>
            <span className="section-index">RESEARCH / 002</span>
            <h2>Enter your next question.</h2>
          </div>
          <span className="workspace-tag">
            <i /> EVIDENCE-FIRST MODE
          </span>
        </div>

        <div className="workspace-grid">
          <aside className="document-library" id="library">
            <div className="panel-heading">
              <span>DOCUMENT LIBRARY</span>
              <span className="panel-index">A / SOURCES</span>
            </div>

            <label className="upload-zone">
              <input
                type="file"
                accept=".pdf,.txt,.md,.docx"
                onChange={handleUpload}
                disabled={uploading}
              />
              <span className="upload-symbol">
                {uploading ? '...' : '+'}
              </span>
              <strong>
                {uploading ? 'Processing document' : 'Add your knowledge'}
              </strong>
              <span>Choose a PDF, TXT, MD or DOCX file</span>
              <span className="upload-link">
                {uploading ? 'PLEASE WAIT' : 'SELECT DOCUMENT ↗'}
              </span>
            </label>

            {uploadMessage && (
              <p className="library-status" role="status">
                {uploadMessage}
              </p>
            )}

            <div className="library-documents">
              {loadingDocuments ? (
                <p className="library-status">Loading documents...</p>
              ) : documentError ? (
                <p className="library-status" role="alert">
                  {documentError}
                </p>
              ) : documents.length === 0 ? (
                <div className="library-empty">
                  <span className="empty-marker" />
                  No indexed documents yet. Upload a document to get started.
                </div>
              ) : (
                <>
                  <div className="library-status">
                    {documents.length} indexed document
                    {documents.length !== 1 ? 's' : ''}
                  </div>

                  {documents.map((document) => (
                    <article
                      className="library-document"
                      key={document.document_id}
                    >
                      <div className="document-file-icon">
                        {document.filename.split('.').pop()?.toUpperCase() || 'FILE'}
                      </div>

                      <div className="document-details">
                        <strong>{document.filename}</strong>
                        <span>
                          {document.chunks_created} chunks ·{' '}
                          {document.extracted_units} extracted units
                        </span>
                        <small>Added {document.created_at}</small>
                      </div>
                    </article>
                  ))}
                </>
              )}
            </div>
          </aside>

          <form
            className="question-panel"
            onSubmit={handleQuestionSubmit}
          >
            <div className="panel-heading">
              <span>ASK YOUR KNOWLEDGE BASE</span>
              <span className="panel-index">B / QUERY</span>
            </div>

            <label className="document-select-label">
              SOURCE DOCUMENT
              <select
                value={selectedDocumentId}
                onChange={(event) =>
                  setSelectedDocumentId(event.target.value)
                }
                disabled={answerLoading || documents.length === 0}
              >
                {documents.length === 0 && (
                  <option value="">No documents available</option>
                )}

                {documents.map((document) => (
                  <option
                    key={document.document_id}
                    value={document.document_id}
                  >
                    {document.filename}
                  </option>
                ))}
              </select>
            </label>

            <textarea
              aria-label="Your research question"
              placeholder="What would you like to discover?"
              rows={4}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />

            <div className="question-guidance">
              <span>Ask a question grounded in your documents.</span>
              <span>NO UNSOURCED CLAIMS</span>
            </div>

            <button
              className="ask-button"
              type="submit"
              disabled={answerLoading || documents.length === 0}
            >
              <span>
                {answerLoading
                  ? 'Analyzing document...'
                  : 'Generate evidence-backed answer'}
              </span>
              <span>{answerLoading ? '...' : '↗'}</span>
            </button>

            {answerError && (
              <div className="answer-panel" role="alert">
                <h3>Unable to generate answer</h3>
                <p>{answerError}</p>
              </div>
            )}
          </form>

          {answerResult && (
            <section className="answer-panel" aria-live="polite">
              <div className="panel-heading">
                <span>GENERATED ANSWER</span>
                <span className="panel-index">
                  {answerResult.citations_valid
                    ? 'CITATIONS VALID'
                    : 'CITATION WARNING'}
                </span>
              </div>

              <p className="answer-question">
                {answerResult.question}
              </p>

              <div className="answer-text">
                {answerResult.answer}
              </div>

              {answerResult.missing_citation && (
                <p className="answer-warning">
                  One or more claims may be missing citations.
                </p>
              )}

              {answerResult.invalid_citation_ids.length > 0 && (
                <p className="answer-warning">
                  Invalid citation IDs:{' '}
                  {answerResult.invalid_citation_ids.join(', ')}
                </p>
              )}

              {answerResult.claim_verifications.length > 0 && (
                <div className="claim-verifications">
                  <h3>Claim verification</h3>

                  {answerResult.claim_verifications.map((claim, index) => (
                    <article
                      className="claim-item"
                      key={`${index}-${claim.claim}`}
                    >
                      <strong>
                        {claim.status.toUpperCase()}: {claim.claim}
                      </strong>
                      <p>{claim.explanation}</p>
                      {claim.evidence_ids.length > 0 && (
                        <small>
                          Evidence: {claim.evidence_ids.join(', ')}
                        </small>
                      )}
                    </article>
                  ))}
                </div>
              )}

              {answerResult.evidence.length > 0 && (
                <div className="answer-evidence">
                  <h3>Source evidence</h3>

                  {answerResult.evidence.map((item) => (
                    <article
                      className="evidence-item"
                      key={item.evidence_id}
                    >
                      <div className="evidence-item-heading">
                        <strong>{item.evidence_id}</strong>
                        <span>{item.source_name}</span>
                        {item.page_number != null && (
                          <span>Page {item.page_number}</span>
                        )}
                      </div>

                      <p>{item.text}</p>
                      <small>
                        Relevance score: {item.relevance_score.toFixed(3)}
                      </small>
                    </article>
                  ))}
                </div>
              )}
            </section>
          )}
        </div>
      </section>

      <footer className="research-footer">
        <a className="footer-logo" href="#top">RAG/CA</a>
        <span>YOUR KNOWLEDGE. TRACEABLE ANSWERS.</span>
        <span className="footer-build">RESEARCH ENGINE / V1.0</span>
      </footer>
    </main>
  )
}

export default App
