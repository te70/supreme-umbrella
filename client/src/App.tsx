import { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

export default function SecureEncryptDecrypt() {

  interface CipherPayload {
  ciphertext: string;
  enc_aes_key: string;
  nonce: string;
  tag: string;
}

  const [plainText, setPlainText] = useState("");
  const [encryptedText, setEncryptedText] = useState("");
  const [cipherPayload, setCipherPayload] = useState<CipherPayload | null>(null);
  const [decryptedText, setDecryptedText] = useState("");

  // Encrypt message via Encrypt API
  const handleEncrypt = async () => {
    if (!plainText.trim()) return;

    try {
      const res = await fetch("http://localhost:8000/encrypt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: plainText }),
      });
      const data = await res.json();
      //show only encrypted text
      setEncryptedText(data.ciphertext);

      //store the full object in hidden state for decryption
      setCipherPayload(data); // auto-fill decrypt box
    } catch (err) {
      console.error("Encryption error:", err);
    }
  };

  // Decrypt message via Decrypt API
  const handleDecrypt = async () => {
    if (!cipherPayload) return;

    try {
      const res = await fetch("http://localhost:8001/decrypt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cipherPayload),
      });
      const data = await res.json();
      setDecryptedText(data.plaintext);
      setEncryptedText(cipherPayload.ciphertext); // keep showing encrypted text
    } catch (err) {
      console.error("Decryption error:", err);
    }
  };

  return (
    <div className="container py-5" style={{ background: "#e0d4f7", minHeight: "100vh" }}>
      <h1 className="text-center mb-5 text-primary">Secure Encrypt/Decrypt</h1>

      {/* Encryption Section */}
      <div className="card mb-4 shadow-sm">
        <div className="card-body">
          <h4 className="card-title text-primary">Encrypt a Message</h4>
          <textarea
            className="form-control mb-3"
            placeholder="Type message here..."
            rows={3}
            value={plainText}
            onChange={(e) => setPlainText(e.target.value)}
          />
          <button className="btn btn-primary" onClick={handleEncrypt}>
            Encrypt
          </button>

          {encryptedText && (
            <div className="card mt-3 bg-light">
              <div className="card-body">
                <h6 className="card-subtitle mb-2 text-muted">Encrypted Message</h6>
                <pre style={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }}>
                  {encryptedText}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Decryption Section */}
      <div className="card shadow-sm">
        <div className="card-body">
          <h4 className="card-title text-success">Decrypt a Message</h4>
          <textarea
            className="form-control mb-3"
            placeholder="Paste encrypted JSON here..."
            rows={5}
            value={encryptedText}
            onChange={(e) => setEncryptedText(e.target.value)}
          />
          <button className="btn btn-success" onClick={handleDecrypt}>
            Decrypt
          </button>

          {decryptedText && (
            <div className="card mt-3 bg-light">
              <div className="card-body">
                <h6 className="card-subtitle mb-2 text-muted">Decrypted Message</h6>
                <p>{decryptedText}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}