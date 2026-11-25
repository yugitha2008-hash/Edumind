import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EduMind – Your Personal AI Learning Assistant</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:#f3f6fc;color:#17233c}
header{background:linear-gradient(120deg,#1746a2,#3979e8);color:white;padding:28px 18px}
header .wrap,main{max-width:900px;margin:auto}h1{margin:0 0 8px;font-size:30px}
header p{margin:0;opacity:.94}.tag{display:inline-block;background:#ffffff22;padding:7px 11px;border-radius:20px;margin-top:14px;font-size:13px}
main{padding:24px 16px}.panel{background:white;border-radius:16px;padding:22px;box-shadow:0 5px 22px #18345b12;margin-bottom:18px}
label{display:block;font-weight:700;margin:13px 0 7px}input,select,textarea{width:100%;padding:12px;border:1px solid #cbd5e1;border-radius:9px;font-size:15px}
textarea{min-height:105px;resize:vertical}button{border:0;border-radius:9px;padding:12px 18px;background:#245dcc;color:white;font-weight:700;font-size:15px;cursor:pointer;margin-top:16px}
button:disabled{opacity:.6;cursor:wait}.answer{white-space:pre-wrap;line-height:1.6;background:#f7f9ff;border-left:4px solid #3979e8;padding:16px;border-radius:8px;margin-top:18px;min-height:45px}
.small{font-size:13px;color:#64748b}.row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:620px){.row{grid-template-columns:1fr}h1{font-size:25px}}
</style>
</head>
<body>
<header><div class="wrap">
<h1>EduMind</h1><p>Your Personal AI Learning Assistant</p>
<span class="tag">Understand Better • Learn Smarter • Grow Confidently</span>
</div></header>
<main>
<section class="panel">
<h2>What would you like to learn today?</h2>
<p class="small">Tell EduMind your learning level and the topic you find difficult. It will explain the concept in simple language and give you a short practice question.</p>
<form id="learnForm">
<div class="row">
<div><label for="level">Class / academic level</label><input id="level" placeholder="e.g. Class 10" required></div>
<div><label for="subject">Subject</label><input id="subject" placeholder="e.g. Science" required></div>
</div>
<label for="topic">Topic you find difficult</label><input id="topic" placeholder="e.g. Photosynthesis" required>
<label for="question">What exactly is confusing? (optional)</label><textarea id="question" placeholder="Tell us what you already understand or where you got stuck."></textarea>
<button id="submitBtn" type="submit">Explain this topic</button>
</form>
<div id="result" class="answer" aria-live="polite">Your explanation will appear here.</div>
<p class="small">For AI answers, the app owner must configure a Gemini API key as the GEMINI_API_KEY environment variable. Do not put API keys in public source code.</p>
</section>
<section class="panel">
<h3>How EduMind helps</h3>
<ul><li>Simple, step-by-step explanations</li><li>Everyday examples</li><li>A quick check-your-understanding question</li><li>Supportive feedback without judgement</li></ul>
</section>
</main>
<script>
const form=document.getElementById('learnForm'), btn=document.getElementById('submitBtn'), result=document.getElementById('result');
form.addEventListener('submit',async e=>{
 e.preventDefault(); btn.disabled=true; btn.textContent='Preparing your explanation...';
 result.textContent='Please wait while EduMind prepares your lesson.';
 try{
  const response=await fetch('/learn',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
   level:document.getElementById('level').value,subject:document.getElementById('subject').value,
   topic:document.getElementById('topic').value,question:document.getElementById('question').value
  })});
  const data=await response.json(); result.textContent=data.answer||data.error||'No response received.';
 }catch(err){result.textContent='Could not connect to EduMind. Please check your internet connection and try again.';}
 finally{btn.disabled=false;btn.textContent='Explain this topic';}
});
</script>
</body></html>
"""

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.post("/learn")
def learn():
    data = request.get_json(silent=True) or {}
    level = str(data.get("level", "")).strip()[:100]
    subject = str(data.get("subject", "")).strip()[:100]
    topic = str(data.get("topic", "")).strip()[:300]
    question = str(data.get("question", "")).strip()[:1000]
    if not level or not subject or not topic:
        return jsonify(error="Please enter your academic level, subject and topic."), 400

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify(error="AI is not connected yet. The app is running, but its owner must configure GEMINI_API_KEY in the deployment environment to enable AI explanations."), 503

    prompt = f"""You are EduMind, a patient and supportive learning assistant.
Help a student at {level} understand the subject {subject}, topic: {topic}.
What the student finds confusing: {question or "Not specified"}.
Use simple age-appropriate language, explain step by step, give one everyday example,
then provide a short summary and one practice question. Do not simply give homework
answers without explaining the reasoning. If unsure about a fact, say so."""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    try:
        r = requests.post(url, params={"key": api_key},
            json={"contents":[{"parts":[{"text":prompt}]}]},
            timeout=45)
        r.raise_for_status()
        payload = r.json()
        answer = payload["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify(answer=answer)
    except requests.RequestException:
        return jsonify(error="The AI service could not be reached. Please check the API key, network and model access."), 502
    except (KeyError, IndexError, TypeError):
        return jsonify(error="The AI service returned an unexpected response. Please try again."), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
