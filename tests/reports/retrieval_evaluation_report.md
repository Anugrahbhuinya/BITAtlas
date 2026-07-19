# RAG Retrieval Quality Evaluation Report

Generated at: 2026-07-14 23:29:17

## 1. Executive Summary Metrics
| Retrieval Metric | Score / Value |
| :--- | :--- |
| **Precision@1 (Accuracy)** | **96.08%** |
| Precision@3 | 89.05% |
| Precision@5 | 89.05% |
| **Mean Reciprocal Rank (MRR)** | **0.9657** |
| **NDCG@5** | **0.967** |
| Average Retrieval Latency | 54.61 ms |
| Average Similarity Score | 0.7984 |

## 2. Details of 100 Campus Queries Benchmark
| # | Query | Expected Category | Retrieved Doc | Actual Source | Sim Score | Result |
| --- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | When do placements begin? | Placement | Placements | kb_document | 0.7658 | ✅ Correct |
| 2 | How does the Placement Cell coordinate student recruitments? | Placement | unknown | faq | 0.9619 | ✅ Correct |
| 3 | Which companies visit the campus for placements? | Placement | Placement and Training Cell | facility | 0.8847 | ✅ Correct |
| 4 | What is the average package and placement rate for B.Tech CSE? | Placement | unknown | faq | 0.9807 | ✅ Correct |
| 5 | Placement and Training Cell location | Placement | Placement and Training Cell | facility | 1.006 | ✅ Correct |
| 6 | placements 2026 batch recruitment | Placement | Placements | kb_document | 1.0644 | ✅ Correct |
| 7 | Who is eligible to participate in the campus placement process? | Placement | unknown | faq | 0.9878 | ✅ Correct |
| 8 | What is the 'One Student, One Job' policy at BIT Mesra? | Placement | unknown | faq | 0.9803 | ✅ Correct |
| 9 | How do I write an academic resume for placements? | Placement | unknown | faq | 0.9436 | ✅ Correct |
| 10 | What industries visit BIT Mesra for mechanical and civil core roles? | Placement | unknown | faq | 0.988 | ✅ Correct |
| 11 | What should I do if my hostel room requires maintenance or repairs? | Hostel | unknown | faq | 0.9947 | ✅ Correct |
| 12 | How are single rooms allocated in senior hostels? | Hostel | Sarojini Hostel | hostel | 1.0166 | ❌ Incorrect |
| 13 | What are the hostel room allocation rules for freshers? | Hostel | unknown | faq | 0.978 | ✅ Correct |
| 14 | What is the procedure to apply for hostel leave? | Hostel | unknown | faq | 0.9997 | ✅ Correct |
| 15 | Hostel Fee Payment Reminder notice | Hostel | unknown | notice | 1.0458 | ✅ Correct |
| 16 | Raman Hostel room details | Hostel | Raman Hostel | hostel | 1.0585 | ✅ Correct |
| 17 | CV Raman Hostel facilities | Hostel | CV Raman Hostel | hostel | 1.0239 | ✅ Correct |
| 18 | Sarojini Hostel for girls | Hostel | Sarojini Hostel | hostel | 1.034 | ✅ Correct |
| 19 | Central Library building location | Library | Central Library | building | 1.0612 | ✅ Correct |
| 20 | What are the membership rules and timings for the Central Library? | Library | unknown | faq | 0.9778 | ✅ Correct |
| 21 | How can I obtain a physical duplicate library card? | Library | unknown | faq | 0.992 | ✅ Correct |
| 22 | Library Timing Extension notice | Library | unknown | notice | 1.0391 | ✅ Correct |
| 23 | Are there scholarships available for merit students? | Scholarship | unknown | faq | 0.971 | ✅ Correct |
| 24 | How do I apply for the e-Kalyan state scholarship? | Scholarship | unknown | faq | 0.9831 | ✅ Correct |
| 25 | Scholarship Application Notice deadline | Scholarship | unknown | notice | 0.9875 | ✅ Correct |
| 26 | International Students Hostel occupancy | Admission | International Students Hostel | hostel | 1.0388 | ✅ Correct |
| 27 | PhD admission application deadline notice | Admission | unknown | notice | 0.5645 | ✅ Correct |
| 28 | Department of Computer Science and Engineering | Department | Computer Science and Engineering | department | 0.9898 | ✅ Correct |
| 29 | Department of Electronics and Communication Engineering | Department | Electronics and Communication Engineering | department | 0.9897 | ✅ Correct |
| 30 | Department of Biotechnology course details | Department | Biotechnology | department | 0.9633 | ✅ Correct |
| 31 | Department of Mechanical Engineering building | Department | Mechanical Engineering | department | 0.9892 | ✅ Correct |
| 32 | Department of Civil Engineering building | Department | Civil Engineering | department | 0.9897 | ✅ Correct |
| 33 | Department of Artificial Intelligence and Machine Learning | Department | Artificial Intelligence and Machine Learning | department | 0.9898 | ✅ Correct |
| 34 | How to contact Dean Academic Affairs? | Faculty | unknown | faq | 0.4995 | ✅ Correct |
| 35 | Dean Student Welfare office hours | Faculty | Student Store | facility | 0.4979 | ❌ Incorrect |
| 36 | professor in charge of placements contact | Faculty | Placements | kb_document | 0.6179 | ✅ Correct |
| 37 | how to join robotics club | Club | Robotics Club | club | 1.0495 | ✅ Correct |
| 38 | AI and Data Science Club activities | Club | AI and Data Science Club | club | 1.0823 | ✅ Correct |
| 39 | music club auditions and schedule | Club | Dance Club | club | 0.6868 | ✅ Correct |
| 40 | Coding Club activities and membership | Club | Coding Club | club | 1.0689 | ✅ Correct |
| 41 | Sports Club tourneys | Club | Sports Club | club | 1.0377 | ✅ Correct |
| 42 | Dance Club auditions | Club | Dance Club | club | 1.0915 | ✅ Correct |
| 43 | Developer Student Club recruitments | Club | Developer Student Club | club | 1.0668 | ✅ Correct |
| 44 | Entrepreneurship Cell startup support | Club | Entrepreneurship Cell | club | 0.9534 | ✅ Correct |
| 45 | Club Recruitment Drive notice | Club | unknown | notice | 0.9858 | ✅ Correct |
| 46 | Technical Fest Announcement notice | Event | unknown | notice | 0.962 | ✅ Correct |
| 47 | Sports Tournament Registration notice | Event | unknown | notice | 0.9448 | ✅ Correct |
| 48 | Hackathon Registration Open notice | Event | unknown | notice | 0.9625 | ✅ Correct |
| 49 | Workshop on Artificial Intelligence notice | Event | unknown | notice | 0.9566 | ✅ Correct |
| 50 | Class commencement date academic calendar | Academic | unknown | calendar | 0.9522 | ✅ Correct |
| 51 | Mid Semester Examination date | Academic | unknown | calendar | 0.9954 | ✅ Correct |
| 52 | End Semester Examination date | Academic | unknown | calendar | 0.9889 | ✅ Correct |
| 53 | Make-Up Examination Registration calendar | Academic | unknown | calendar | 0.9939 | ✅ Correct |
| 54 | Semester Registration Notice deadline | Academic | unknown | notice | 1.064 | ✅ Correct |
| 55 | Semester Result Declaration notice | Academic | unknown | notice | 1.0461 | ✅ Correct |
| 56 | Minor Project Evaluation Schedule notice | Academic | unknown | notice | 1.0172 | ✅ Correct |
| 57 | Attendance Shortage Notification notice | Academic | unknown | notice | 0.9623 | ✅ Correct |
| 58 | What is the rule for makeup or supplementary examinations? | Academic | unknown | faq | 1.0062 | ✅ Correct |
| 59 | What is the minimum attendance requirement to write examinations? | Academic | unknown | faq | 0.9852 | ✅ Correct |
| 60 | How is the CGPA calculated at the end of a semester? | Academic | unknown | faq | 0.9802 | ✅ Correct |
| 61 | How can I change my branch or engineering stream after the first year? | Academic | unknown | faq | 0.9956 | ✅ Correct |
| 62 | Main Administrative Building location | Policy | Main Administrative Building | building | 0.9898 | ✅ Correct |
| 63 | Lecture Hall Complex building | Policy | Lecture Hall Complex | building | 0.9898 | ✅ Correct |
| 64 | Sports Complex facilities | Policy | Sports Complex | building | 0.9675 | ✅ Correct |
| 65 | Student Activity Center building | Policy | Student Activity Center | building | 1.0232 | ✅ Correct |
| 66 | University Auditorium building | Policy | University Auditorium | building | 0.9899 | ✅ Correct |
| 67 | Research and Innovation Center building | Policy | Research and Innovation Center | building | 0.9898 | ✅ Correct |
| 68 | Guest House facilities for visitors | Policy | Guest House | building | 0.9596 | ✅ Correct |
| 69 | Are there guest house booking facilities for students' families? | Policy | unknown | faq | 0.975 | ✅ Correct |
| 70 | Medical Unit facility and doctor timings | Policy | Medical Unit | facility | 0.9786 | ✅ Correct |
| 71 | Campus Gymnasium fees and equipment | Policy | Campus Gymnasium | facility | 0.8649 | ✅ Correct |
| 72 | SBI Bank Branch location on campus | Policy | SBI Bank Branch | facility | 0.9629 | ✅ Correct |
| 73 | SBI ATM location | Policy | SBI ATM | facility | 0.9791 | ✅ Correct |
| 74 | Indoor Sports Hall facilities | Policy | Indoor Sports Hall | facility | 0.9465 | ✅ Correct |
| 75 | Stationery and Xerox Center facilities | Policy | Stationery and Xerox Center | facility | 0.9571 | ✅ Correct |
| 76 | Nescafe Outlet location | Policy | Nescafe Outlet | facility | 0.9765 | ✅ Correct |
| 77 | Central Cafeteria menu and location | Policy | Central Cafeteria | facility | 0.9629 | ✅ Correct |
| 78 | Student Store items | Policy | Student Store | facility | 0.9437 | ✅ Correct |
| 79 | Is there a postal and courier service office on campus? | Policy | unknown | faq | 0.9735 | ✅ Correct |
| 80 | How is the hostel mess fee collected and managed? | Hostel | unknown | faq | 0.9875 | ✅ Correct |
| 81 | What is the policy regarding medical leave and mess reduction? | Hostel | Aryabhatta Hostel | hostel | 0.573 | ❌ Incorrect |
| 82 | Who manages the hostel mess operations? | Hostel | Aryabhatta Hostel | hostel | 0.8711 | ❌ Incorrect |
| 83 | What public transport options connect the campus to Ranchi? | Transport | unknown | faq | 0.9735 | ✅ Correct |
| 84 | campus shuttle timing and route | Transport | Campus Gymnasium | facility | 0.5294 | ✅ Correct |
| 85 | Are students allowed to keep private vehicles on campus? | Transport | unknown | faq | 0.8524 | ✅ Correct |
| 86 | Is there a cycle sharing scheme on campus? | Transport | unknown | faq | 0.5026 | ✅ Correct |
| 87 | What are the rules regarding student vehicle parking? | Transport | unknown | faq | 0.5248 | ✅ Correct |
| 88 | What constitutes ragging according to the campus policy? | Policy | unknown | faq | 0.7317 | ✅ Correct |
| 89 | How do I reset my ERP portal password? | FAQ | unknown | faq | 0.995 | ✅ Correct |
| 90 | Where can I view my daily attendance records in ERP? | FAQ | unknown | faq | 0.9159 | ✅ Correct |
| 91 | What is the procedure to get a duplicate student ID card? | FAQ | unknown | faq | 0.933 | ✅ Correct |
| 92 | What happens if I fail a course and get an F grade? | FAQ | unknown | faq | 0.5025 | ✅ Correct |
| 93 | How do I apply for official academic transcripts? | FAQ | unknown | faq | 0.9253 | ✅ Correct |
| 94 | what is the fee structure for BTech program? | FAQ | unknown | faq | 0.499 | ✅ Correct |
| 95 | What is the refund policy on course cancellation? | FAQ | unknown | faq | 0.5045 | ✅ Correct |
| 96 | minimum attendance requirement and medical leave relaxation | Academic | unknown | faq | 0.5075 | ✅ Correct |
| 97 | What are the student insurance coverage details? | FAQ | unknown | faq | 0.5041 | ✅ Correct |
| 98 | What are the consequences of violating the placement code of conduct? | FAQ | unknown | faq | 0.9696 | ✅ Correct |
| 99 | What is the campus dress code for academic classes? | FAQ | unknown | faq | 0.9792 | ✅ Correct |
| 100 | ERP Maintenance Window notice | Notice | unknown | notice | 0.9595 | ✅ Correct |
| 101 | Campus WiFi Upgrade notice | Notice | unknown | notice | 0.9632 | ✅ Correct |
| 102 | Medical Camp on Campus notice | Notice | unknown | notice | 0.957 | ✅ Correct |
