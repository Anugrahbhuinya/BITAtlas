import io
import sys
from app.services.rag.rag_service import query_rag

# Ensure UTF-8 output on Windows standard terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print(query_rag("scholarship notice"))
print()
print(query_rag("placement training"))
print()
print(query_rag("hackathon"))
print()
print(query_rag("hostel fee"))
print(query_rag("Where is the Central Library?"))
print(query_rag("Tell me about Aryabhatta Hostel"))
print(query_rag("Which department offers AIML?"))
print(query_rag("What clubs are available?"))
print(query_rag("Medical Center"))
print()
print(query_rag("When is Quiz1?"))
print()
print(query_rag("What is the academic calendar?"))
print()
print(query_rag("When is End Semester Examination?"))