from typing import Any, List

from pydantic import BaseModel

from phi.document.base import Document


class Reader(BaseModel):
    chunk: bool = True
    chunk_size: int = 500
    separators: List[str] = ["\n", "\r\n", "\r", " \n"]

    def read(self, obj: Any) -> List[Document]:
        raise NotImplementedError

    def chunk_text(self, text: str) -> List[str]:
        import re

        # Join the separators with the '|' symbol to create a regex pattern
        regex_pattern = "|".join(map(re.escape, self.separators))

        # Split the text using the regex pattern
        chunks = re.split(regex_pattern, text)

        return chunks

    def chunk_document(self, document: Document) -> List[Document]:
        # Chunk the document content
        chunks = self.chunk_text(document.content)

        # Create a list of chunked documents
        chunked_documents: List[Document] = []

        chunk_start = 1
        chunked_text = ""
        chunk_size = 0
        chunk_source = document.source
        chunk_meta_data = document.meta_data
        for idx, chunk in enumerate(chunks, start=1):
            chunk_size += len(chunk)
            if chunk_size > self.chunk_size:
                meta_data = chunk_meta_data.copy()
                meta_data["chunk"] = chunk_start
                meta_data["chunk_size"] = chunk_size
                chunked_documents.append(
                    Document(
                        content=chunked_text,
                        source=chunk_source,
                        meta_data=meta_data,
                    )
                )
                chunk_start = idx
                chunked_text = ""
                chunk_size = 0
            else:
                chunked_text += chunk

        # Get the last chunk
        if chunked_text:
            meta_data = chunk_meta_data.copy()
            meta_data["chunk"] = chunk_start
            meta_data["chunk_size"] = chunk_size
            chunked_documents.append(
                Document(
                    content=chunked_text,
                    source=chunk_source,
                    meta_data=meta_data,
                )
            )
        return chunked_documents