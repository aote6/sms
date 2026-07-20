from dataclasses import dataclass
from pathlib import Path
import hashlib
import time

@dataclass(slots=True)
class Artifact:
    module: str
    version: str
    language: str
    path: Path
    digest: str
    generated_at: float
    
    @classmethod
    def create(cls, module: str, version: str, language: str, path: Path):
        path = Path(path)
        if path.exists():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            digest = ""
        return cls(
            module=module,
            version=version,
            language=language,
            path=path,
            digest=digest,
            generated_at=time.time()
        )
    
    def exists(self) -> bool:
        return self.path.exists()
    
    def to_dict(self):
        return {
            "module": self.module,
            "version": self.version,
            "language": self.language,
            "path": str(self.path),
            "digest": self.digest,
            "generated_at": self.generated_at
        }
