from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
from typing import List, Dict, Union

class QuestionGenerator:
    def __init__(self):
        model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        cache_dir = "D:/huggingface_cache"

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        print(f"⚡ Model is running on: {self.device} ({dtype})")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id, 
            cache_dir=cache_dir,
            padding_side="left",
            truncation=True
        )
<<<<<<< HEAD

=======
        
>>>>>>> d5149f326e8f0ab22c2dfa1ba991c11400a0bf57
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            cache_dir=cache_dir,
            torch_dtype=dtype,
            device_map="auto",
            low_cpu_mem_usage=True
        ).to(self.device)
<<<<<<< HEAD

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    # --------------------------------------------------------------------------
    # UPDATED PART — Better Question Generation (rest of class unchanged)
    # --------------------------------------------------------------------------
    def generate(self, resume_summary: str) -> List[str]:
        prompt = (
            f"<|system|>\n"
            f"You are a senior technical interviewer.\n"
            f"Generate **5 high-quality technical interview questions** based ONLY on the candidate's resume below.\n\n"
            f"Resume Summary:\n{resume_summary}\n\n"
            f"IMPORTANT RULES:\n"
            f"- Ask ONLY proper interview questions.\n"
            f"- Do NOT repeat resume sentences.\n"
            f"- Do NOT convert statements into questions.\n"
            f"- Ask domain-relevant questions (AI/ML/Data/Python/SQL/Web etc.).\n"
            f"- Each question MUST be direct, meaningful, and interview-ready.\n"
            f"- Return ONLY a numbered list (1-5).\n"
            f"- No explanations.\n</s>\n"
            f"<|user|>\nGenerate the questions.\n</s>\n"
=======
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate(self, resume_summary: str) -> List[str]:
        prompt = (
            f"<|system|>\n"
            f"You are a technical interviewer analyzing a resume. Generate 5 technical interview questions "
            f"based on these skills and experiences:\n\n"
            f"{resume_summary}\n\n"
            f"Return ONLY a numbered list of questions (1-5) with no additional text or explanations.</s>\n"
            f"<|user|>\n"
            f"Please generate the questions now.</s>\n"
>>>>>>> d5149f326e8f0ab22c2dfa1ba991c11400a0bf57
            f"<|assistant|>\n"
        )

        inputs = self.tokenizer(
            str(prompt),
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding=True
        ).to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            num_return_sequences=1
        )

        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[-1]:],
            skip_special_tokens=True
        )

        questions = []
<<<<<<< HEAD
        for q in response.split("\n"):
            q = q.strip()
            if not q:
                continue

            # remove numbering
            if q[0].isdigit() and ('.' in q or ')' in q):
                q = q.split('.', 1)[-1].split(')', 1)[-1].strip()

            # force question format
            if not q.endswith('?'):
                q += '?'

            # filter out junk lines
            if len(q) < 10:
                continue

            questions.append(q)

        return questions[:5] or [
            "Can you explain your experience with machine learning projects?",
            "What challenges have you solved using Python?",
            "How do you optimize SQL queries for performance?",
            "Explain a deep learning model you recently implemented.",
            "How do you approach debugging issues in ML pipelines?"
        ]
    # --------------------------------------------------------------------------
=======
        for q in response.split('\n'):
            q = q.strip()
            if not q:
                continue
            if q[0].isdigit() and ('.' in q or ')' in q):
                q = q.split('.', 1)[-1].split(')', 1)[-1].strip()
            if '?' not in q:
                q += '?'
            questions.append(q)
        
        return questions[:5] or ["Can you explain your experience with the technologies mentioned in your resume?"]
>>>>>>> d5149f326e8f0ab22c2dfa1ba991c11400a0bf57

    def generate_follow_up(self, context: str) -> str:
        prompt = (
            f"<|system|>\n"
            f"You are conducting a technical interview. Generate one insightful follow-up question "
            f"based on this conversation context:\n\n"
            f"{context}\n\n"
            f"Return ONLY the question with no additional text or numbering.</s>\n"
            f"<|user|>\n"
            f"Please generate the follow-up question now.</s>\n"
            f"<|assistant|>\n"
        )

        inputs = self.tokenizer(
            str(prompt),
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding=True
        ).to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[-1]:],
            skip_special_tokens=True
        ).strip()

        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
            line = line.strip('"\'')
            if '?' in line:
                return line.rstrip('?') + '?'
            elif line.endswith('.'):
                return line[:-1] + '?'
        
        return "Could you elaborate on that point further?"

    def review_answer(self, qa_context: str) -> Dict[str, Union[int, str]]:
        prompt = (
            f"<|system|>\n"
            f"Analyze this interview Q&A and provide:\n"
            f"- Technical accuracy score (0-100)\n"
            f"- Relevance score (0-100)\n"
            f"- Confidence score (0-100)\n"
            f"- 3 specific improvement suggestions\n"
            f"- Expected ideal answer summary\n\n"
            f"Context:\n{qa_context}\n\n"
            f"Return JSON format with: technical_score, relevance_score, "
            f"confidence_score, feedback, expected_answer, improvement_suggestions</s>\n"
            f"<|user|>\n"
            f"Please provide the evaluation now.</s>\n"
            f"<|assistant|>\n"
        )

        inputs = self.tokenizer(
            str(prompt),
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding=True
        ).to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=400,
            temperature=0.3,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[-1]:],
            skip_special_tokens=True
        ).strip()

        try:
<<<<<<< HEAD
=======
            # Ensure response is a string and clean
>>>>>>> d5149f326e8f0ab22c2dfa1ba991c11400a0bf57
            if isinstance(response, list):
                response = " ".join(map(str, response))
            feedback_data = json.loads(response)
            for score in ['technical_score', 'relevance_score', 'confidence_score']:
                if score in feedback_data:
                    feedback_data[score] = max(0, min(100, int(feedback_data[score])))
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"⚠️ Error parsing feedback: {e}")
            feedback_data = {
                "technical_score": 70,
                "relevance_score": 75,
                "confidence_score": 65,
                "feedback": "The answer was relevant but could benefit from more specific examples and technical depth.",
                "expected_answer": "A strong answer would demonstrate specific experience with the technologies mentioned and provide concrete examples.",
                "improvement_suggestions": [
                    "Provide more technical details",
                    "Include specific examples",
                    "Structure your answer more clearly"
                ]
            }

        feedback_data["proficiency"] = int(
            (feedback_data["technical_score"] * 0.5) + 
            (feedback_data["relevance_score"] * 0.3) +
            (feedback_data["confidence_score"] * 0.2)
        )

        return feedback_data
