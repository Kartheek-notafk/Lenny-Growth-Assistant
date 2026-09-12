import React, {useState} from "react"
import {createRoot} from "react-dom/client"
import "./style.css"

function App(){
  const [messages,setMessages]=useState([])
  const [input,setInput]=useState("")
  const [artifact,setArtifact]=useState(null)

  async function send(skill=null){
    if(!input.trim()) return
    const user=input
    setInput("")
    setMessages(m=>[...m,{role:"user",content:user}])
    try{
      const r=await fetch("http://localhost:8000/api/chat",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({session_id:"demo-session",message:user,skill})
      })
      const data=await r.json()
      setMessages(m=>[...m,{role:"assistant",content:data.answer,sources:data.sources||[]}])
      if(data.artifact) setArtifact(data.artifact)
    }catch(e){
      setMessages(m=>[...m,{role:"assistant",content:"Backend unavailable. Check FastAPI and Ollama."}])
    }
  }

  return <div className="app">
    <header><h1>The Lenny Growth Assistant</h1><span>Provider: Ollama</span></header>
    <main>
      <section className="chat">
        <div className="messages">
          {messages.map((m,i)=><div className={"msg "+m.role} key={i}>
            <b>{m.role==="user"?"You":"Assistant"}</b>
            <div>{m.content}</div>
            {m.sources?.length>0 && <details><summary>Sources</summary>{m.sources.map((s,j)=><div className="source" key={j}><b>{s.title}</b> — {s.snippet}</div>)}</details>}
          </div>)}
        </div>
        <div className="composer">
          <textarea value={input} onChange={e=>setInput(e.target.value)} placeholder="Ask a product or growth question..." />
          <div>
            <button onClick={()=>send()}>Ask</button>
            <button onClick={()=>send("ship30")}>Ship 30 Essay</button>
            <button onClick={()=>send("artifact")}>Create Artifact</button>
          </div>
        </div>
      </section>
      <aside>
        <h2>Artifact Viewer</h2>
        {artifact ? <iframe title="artifact" sandbox="" srcDoc={artifact}/> : <p>Generated Markdown/HTML will appear here.</p>}
      </aside>
    </main>
  </div>
}
createRoot(document.getElementById("root")).render(<App/>)
