from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# ==== Request / Response Modelle (möglichst nah an deinem .NET-Modell) ====

class PromptInspectionMeta(BaseModel):
    userId: Optional[str] = None
    source: Optional[str] = None


class PromptInspectionRequest(BaseModel):
    prompt: str
    meta: Optional[PromptInspectionMeta] = None


class Finding(BaseModel):
    type: str
    message: str


class PromptInspectionResponse(BaseModel):
    isAllowed: bool  # True | False
    findings: List[Finding]


# ==== Echo-Logik ====
@app.post("/inspect", response_model=PromptInspectionResponse)
async def inspect(req: PromptInspectionRequest):
    """
    Echo-PromptInsepction-Service:
    - allows all prompts by default
    - adds a demo finding if the prompt contains the word "block"
    """

    findings: List[Finding] = []

    isallowed = True
    if "block" in req.prompt.lower():
        isallowed = False
        findings.append(Finding(
            type="demo_rule",
            message="Prompt contains the word 'block', demo decision=block"
        ))

    # Debug-Finding with Meta-Infos
    findings.append(Finding(
        type="echo_meta",
        message=f"userId={req.meta.userId if req.meta else None}, source={req.meta.source if req.meta else None}"
    ))

    return PromptInspectionResponse(
        isAllowed=isallowed,
        findings=findings
    )
