# Unit Test Suite Report

Generated at: 2026-07-15 00:32:26
**Status**: PASSED
**Exit Code**: 0

## Test Execution Details
```text
C:\Users\ASUS\anaconda3\Lib\site-packages\pytest_asyncio\plugin.py:208: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-8.3.3, pluggy-1.5.0 -- C:\Users\ASUS\anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\ASUS\bit-mesra-ai-agent\tests
configfile: pytest.ini
plugins: anyio-4.13.0, langsmith-0.8.9, locust-2.44.4, asyncio-0.24.0, cov-7.1.0
asyncio: mode=Mode.AUTO, default_loop_scope=None
collecting ... collected 108 items / 98 deselected / 10 selected

tests\unit\test_intent_prompt_context.py::test_intent_classification PASSED [ 10%]
tests\unit\test_intent_prompt_context.py::test_routing_decision_making PASSED [ 20%]
tests\unit\test_intent_prompt_context.py::test_prompt_builder PASSED     [ 30%]
tests\unit\test_intent_prompt_context.py::test_context_engine_deduplicator PASSED [ 40%]
tests\unit\test_intent_prompt_context.py::test_context_engine_prioritizer PASSED [ 50%]
tests\unit\test_workspace_auth_admin.py::test_jwt_authentication_token_cycle PASSED [ 60%]
tests\unit\test_workspace_auth_admin.py::test_jwt_expired_token_handling PASSED [ 70%]
tests\unit\test_workspace_auth_admin.py::test_tokenizer_token_counting PASSED [ 80%]
tests\unit\test_workspace_auth_admin.py::test_jaccard_similarity_edge_cases PASSED [ 90%]
tests\unit\test_workspace_auth_admin.py::test_website_content_normalizer PASSED [100%]

=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.13.5-final-0 _______________

Name                                                              Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------------------------------------------------
backend\app\auth\jwt_service.py                                      30      6      6      3    75%   32-39, 51, 53, 58
backend\app\auth\password_service.py                                  2      0      0      0   100%
backend\app\auth\repository.py                                       20     10      0      0    50%   7, 13-14, 20, 26-27, 33-34, 40-41
backend\app\auth\routes.py                                           40     17      2      0    55%   22, 25, 35-36, 48-51, 67-74, 86-90, 102
backend\app\auth\schemas.py                                          24      4      2      0    77%   13-16
backend\app\auth\service.py                                          48     33      8      0    27%   13, 17-18, 77-78, 84-140, 147, 153-154
backend\app\context\academic_context_provider.py                     10      5      2      0    42%   6, 10-20
backend\app\context\attendance_context_provider.py                   31     26      8      0    13%   6, 10-61
backend\app\context\calendar_context_provider.py                     17     12      4      0    24%   8-28
backend\app\context\planner_context_provider.py                      36     30     14      0    12%   7, 11-66
backend\app\context\student_context_provider.py                       7      4      2      0    33%   6-15
backend\app\context\timetable_context_provider.py                    34     27     14      0    15%   8, 12-64
backend\app\core\auth.py                                             35     24      8      0    26%   31-43, 49-86
backend\app\core\port_checker.py                                     57     46     32      2    17%   12, 17-73
backend\app\core\prompt_config.py                                     8      0      0      0   100%
backend\app\data_loader.py                                            0      0      0      0   100%
backend\app\middleware\auth.py                                       67     53     28      0    15%   18-29, 39-109, 119-124, 130-135, 141
backend\app\models\academic_workspace.py                             33      9      0      0    73%   15-22, 28
backend\app\models\admin.py                                          53      0      0      0   100%
backend\app\models\attendance.py                                     95     23      0      0    76%   25-38, 41, 69-75, 78
backend\app\models\knowledge.py                                     112      0      0      0   100%
backend\app\models\planner.py                                        69     14      0      0    80%   23-35, 38
backend\app\models\schemas.py                                        16      0      0      0   100%
backend\app\models\timetable.py                                      73      9      0      0    88%   27-34, 40
backend\app\models\website.py                                        45      0      0      0   100%
backend\app\models\website_sync.py                                   69      0      0      0   100%
backend\app\navigation\ai\context_provider.py                        92     75     24      0    15%   22-35, 47-171
backend\app\navigation\ai\services\campus_insight.py                 20     17     10      0    10%   16-46
backend\app\navigation\ai\services\departure_advisor.py              33     29     10      0     9%   17-63
backend\app\navigation\ai\services\nearby.py                         33     26     12      0    16%   9, 13-21, 24-70
backend\app\navigation\ai\services\reasoning.py                      29     26     14      0     7%   16-61
backend\app\navigation\ai\services\recommendation.py                 26     22     18      0     9%   10-43, 57-80
backend\app\navigation\constants.py                                  51      0      0      0   100%
backend\app\navigation\dependencies.py                               27     11      0      0    59%   25, 28, 31, 34, 37, 41, 47, 50, 53, 56, 64
backend\app\navigation\graph\models.py                               40     14      0      0    65%   36-41, 44, 65-70, 73
backend\app\navigation\graph\repositories.py                         58     36     14      0    31%   22-27, 30-44, 47, 50, 53, 57-63, 66-72, 76, 82
backend\app\navigation\graph\routes.py                               61     31      2      0    48%   32-34, 37-38, 47-50, 59-60, 68-69, 78-84, 93-94, 103-104, 114-115, 124-125, 136-142
backend\app\navigation\graph\schemas.py                              37      0      0      0   100%
backend\app\navigation\graph\services.py                            406    381    138      0     5%   16-17, 21-577, 580-819, 824-825, 828-829, 832-833, 836-840, 843-844, 847-848, 851-853, 856-858, 861-873, 876-884, 887-901
backend\app\navigation\graph\utils.py                                73     67     44      0     5%   9, 12-136
backend\app\navigation\models.py                                     78     60      0      0    23%   28-44, 47, 83-94, 97, 124-131, 134, 158-166, 169, 194-202, 205
backend\app\navigation\repositories.py                              256    210     72      0    14%   9, 12-18, 21-24, 33-49, 52-63, 66-68, 71-78, 81-85, 90, 93-99, 110-129, 138-152, 155-160, 163-165, 168-175, 178-182, 185-186, 191, 194-200, 209-222, 225-233, 236-238, 241-248, 251-255, 260, 263-269, 278-292, 295-304, 307-309, 312-319, 322-326, 331, 334-340, 349-359, 362-367, 370-372, 375-382, 385-389
backend\app\navigation\routes.py                                     97     32      0      0    67%   58, 67, 76, 85, 95, 104-105, 122, 131, 140, 150, 159-160, 175, 184, 193, 203, 212-213, 228, 237, 246, 256, 265-266, 281, 290, 299, 309, 318-319, 332
backend\app\navigation\routing\algorithms\accessible_route.py        25     18     12      0    19%   17-43
backend\app\navigation\routing\algorithms\fastest_route.py           34     27     18      0    13%   17-54
backend\app\navigation\routing\algorithms\shortest_path.py           23     16     10      0    21%   17-39
backend\app\navigation\routing\interfaces\strategy.py                 7      0      0      0   100%
backend\app\navigation\routing\models\route.py                       15     11      0      0    27%   21-31
backend\app\navigation\routing\repositories\route_cache.py           20      9      0      0    55%   12-14, 17-19, 22-23, 29
backend\app\navigation\routing\routes.py                             58     34      6      0    38%   28-36, 49-72, 87-102, 117-126, 140-148, 164-165
backend\app\navigation\routing\schemas\route.py                      31      0      0      0   100%
backend\app\navigation\routing\services\eta.py                       21     16     10      0    16%   8, 15-34
backend\app\navigation\routing\services\instruction.py               77     70     42      0     6%   10-16, 19-34, 37-99
backend\app\navigation\routing\services\routing.py                  115     99     40      0    10%   23-29, 42-151, 157-172, 178-197
backend\app\navigation\routing\validators\route_validator.py         14      9      6      0    25%   17-28
backend\app\navigation\schemas.py                                   199     14      8      0    89%   140-146, 184-190
backend\app\navigation\services.py                                  212    157     74      0    19%   35-41, 44-50, 59-61, 70-94, 97-115, 118-119, 128-134, 145-147, 156-184, 187-213, 216-217, 225-231, 240-242, 250-261, 264-278, 281-282, 290-296, 305-307, 315-327, 330-346, 349-350, 355, 358-364, 373-375, 383-394, 397-413, 416-417, 434-544
backend\app\navigation\validators.py                                 21     21     14      0     0%   3-36
backend\app\repositories\academic_repository.py                      21     13      0      0    38%   7, 13-16, 22-24, 30-37
backend\app\repositories\attendance_repository.py                   102     84     20      0    15%   7-8, 14-20, 24-33, 37-47, 51-59, 64-66, 70-77, 83-86, 90-96, 100-109, 113-126, 130-133, 137-144, 148-152
backend\app\repositories\planner_repository.py                       50     39      6      0    20%   7, 11-17, 21-29, 33-35, 39-46, 50-54, 58-69
backend\app\repositories\timetable_repository.py                     20     13      0      0    35%   6, 12-15, 21-23, 29-36
backend\app\routes\academic_dashboard.py                             30     14      2      0    50%   21-34, 50-58
backend\app\routes\academics.py                                      41     27      0      0    34%   20, 30-34, 48-53, 65-98
backend\app\routes\admin.py                                         115     78     30      0    26%   47-77, 84-85, 89-90, 94-95, 99-100, 104-105, 109-110, 114-115, 129-144, 157-163, 175-181, 193-268
backend\app\routes\attendance.py                                     35     11      0      0    69%   25-28, 36, 44, 53, 62, 72, 81, 89
backend\app\routes\chat.py                                          525    495    162      0     4%   71-77, 134-162, 169-187, 190-196, 214-251, 262-1170
backend\app\routes\history.py                                        17      9      2      0    42%   12-23, 29-33
backend\app\routes\knowledge.py                                     109     66     14      0    35%   31-33, 54-64, 74-75, 95-107, 120-126, 134-143, 156-162, 169-176, 188-195, 207-214, 226-227, 240-249, 270-288, 301-302, 306-307, 311-312, 316-317
backend\app\routes\planner.py                                        42     15      0      0    64%   26-28, 31-35, 43, 52, 62, 71, 80, 88, 96
backend\app\routes\timetable.py                                      47     21      2      0    53%   26, 36-37, 47-48, 58-59, 70-71, 83-84, 95-96, 107-123, 138-139
backend\app\routes\websites.py                                      109     73     18      0    28%   31-38, 53-55, 67-68, 80-104, 121-128, 141-148, 160-162, 175-182, 199-208, 224-233, 250-262, 278-282
backend\app\schemas\prompt_schema.py                                 48      0      0      0   100%
backend\app\security\config\settings.py                              75      8     12      3    83%   78->77, 90-94, 102, 110, 112
backend\app\security\core\exceptions\handlers.py                     34     23     10      0    25%   13-21, 32-40, 50-72, 85-104
backend\app\security\core\exceptions\responses.py                     8      4      2      0    40%   18-29
backend\app\security\core\middleware\logging.py                      18     11      0      0    39%   14-50
backend\app\security\core\middleware\request_id.py                   10      5      0      0    50%   11-16
backend\app\security\core\middleware\security.py                     16     11      4      0    25%   10-29
backend\app\security\core\middleware\timing.py                       10      5      0      0    50%   11-15
backend\app\security\monitoring\health.py                            59     43      4      0    25%   16, 29-78, 96, 112-153
backend\app\security\monitoring\logging.py                           34      5     16      5    80%   25, 30, 40, 44, 50
backend\app\security\permissions.py                                  14      4      2      0    62%   13-19
backend\app\security\rate_limit\rate_limiter.py                      99     71     36      0    21%   10-15, 30-47, 59-111, 125-131, 154, 165-167, 175, 186, 197, 208, 219-221
backend\app\security\sanitizers\ai_guard.py                          21     13      8      0    28%   28-46, 56-64
backend\app\services\academic_context_service.py                    159    147     74      0     5%   22-28, 33-74, 86-243
backend\app\services\academic_dashboard_service.py                   75     60     16      0    16%   11-12, 22-25, 32-92, 115-177, 182, 186-193
backend\app\services\academic_workspace_service.py                   36     26     10      0    22%   10, 16-36, 46-68, 78-92
backend\app\services\admin_service.py                               143    129     38      0     8%   15-46, 54-62, 70-174, 187-242, 248-286, 292-389, 395-398
backend\app\services\ai\cache.py                                     45     28     10      0    31%   14-16, 19-32, 35-42, 45-47, 53, 56, 59
backend\app\services\ai\prompt\builder.py                           262     47    116     27    74%   128-142, 145-147, 195-197, 224, 229->231, 239->241, 241->243, 243->245, 249, 250->252, 252->256, 258-260, 267->276, 276->304, 292->298, 295->298, 305->311, 311->313, 313->exit, 324->322, 334, 343, 347, 353-365, 368, 377, 378->374, 382-391, 392->374, 397->340
backend\app\services\ai\prompt\compression.py                        82     22     40      8    67%   21-22, 54-74, 81, 100, 109-110, 112->106, 124, 136->130
backend\app\services\ai\prompt\examples.py                           27      1      4      1    94%   105
backend\app\services\ai\prompt\formatter.py                          10      1      2      1    83%   20
backend\app\services\ai\prompt\hallucination.py                       5      0      0      0   100%
backend\app\services\ai\prompt\navigation_resolver.py               211    197    138      0     4%   28-339
backend\app\services\ai\prompt\orchestrator.py                      137     16     32     15    82%   58, 78, 85->87, 88, 89->91, 91->93, 94, 103, 112->116, 121-126, 139->141, 144, 161->176, 172->176, 215-219
backend\app\services\ai\prompt\personas.py                           28      2      6      2    88%   25, 65
backend\app\services\ai\prompt\selector.py                            9      1      2      1    82%   21
backend\app\services\ai\prompt\templates.py                          44     18     12      4    54%   25, 37-39, 46-52, 59-65
backend\app\services\ai\prompt\validator.py                          38     11     18      8    66%   27-28, 32-33, 38-39, 43, 50, 62, 67, 70
backend\app\services\ai\prompt\variables.py                          20      5      8      3    71%   18, 26, 30, 36-38
backend\app\services\attendance_calculator.py                        21     18     12      0     9%   12-47
backend\app\services\attendance_service.py                          288    260    138      0     7%   19, 23, 27-32, 36-37, 44-72, 76-77, 84-113, 117-253, 276-282, 287-348, 352-410, 414-439, 443-530, 542-547, 556, 560-561, 565-576, 580-593
backend\app\services\context\compression.py                          71     61     32      0    10%   59-159, 169-182
backend\app\services\context\configs\context_config.py               29      0      0      0   100%
backend\app\services\context\deduplicator.py                         48     11     24      7    69%   59, 65-66, 69->82, 82->107, 85-100, 105, 111->119
backend\app\services\context\diagnostics.py                          35     25      8      0    23%   30-34, 38-64, 76-109
backend\app\services\context\injector.py                             42     34      8      0    16%   39-106
backend\app\services\context\interfaces.py                           15      3      0      0    80%   41, 50, 60
backend\app\services\context\merger.py                               41     32     20      0    15%   63-118
backend\app\services\context\models.py                              114      7      4      0    91%   87, 165-168, 172-173
backend\app\services\context\orchestrator.py                         34     23      2      0    31%   27-28, 51-131
backend\app\services\context\pipeline.py                             71     48     16      0    26%   54-70, 84-173
backend\app\services\context\prioritizer.py                          39      3      8      2    89%   67-72, 78->82, 150
backend\app\services\context\providers\base.py                       19     11      4      0    35%   47-69, 90-98, 117-125
backend\app\services\context\providers\conversation_provider.py      60     42     18      0    23%   55-63, 77-85, 98, 102, 117-181
backend\app\services\context\providers\navigation_provider.py        60     45     12      0    21%   46, 50, 63-213, 223-224
backend\app\services\context\providers\profile_provider.py           43     28     10      0    28%   41, 45, 57-114
backend\app\services\context\providers\rag_provider.py               53     35     16      0    26%   61, 65, 78-170
backend\app\services\context\providers\system_provider.py            29     13      0      0    55%   43, 47, 59-92
backend\app\services\context\providers\workspace_provider.py         34     19      4      0    39%   42, 46, 58-123
backend\app\services\context\selector.py                             35     25     16      0    20%   81-128
backend\app\services\context\token_budget.py                         58     48     24      0    12%   45-82, 86-149
backend\app\services\context\utils\ranking.py                        21     11      6      1    41%   39-45, 59-61, 80
backend\app\services\context\utils\similarity.py                     28      3      6      2    85%   55, 61, 80
backend\app\services\context\utils\tokenizer.py                       8      2      2      0    80%   39, 52
backend\app\services\history_service.py                              40     34     12      0    12%   5-16, 27-40, 43-47, 55-65
backend\app\services\knowledge\docx_processor.py                     23     18     12      0    14%   12-36
backend\app\services\knowledge\file_upload_service.py                43     32     14      0    19%   13-15, 31-93
backend\app\services\knowledge\knowledge_service.py                 246    220     84      0     8%   18-57, 61-74, 79-142, 145-215, 218-239, 242-243, 246-270, 278-300, 303-367, 370-436, 456-464, 467-475, 478-486, 489-517
backend\app\services\knowledge\markdown_processor.py                 17     12      0      0    29%   12-33
backend\app\services\knowledge\txt_processor.py                      10      7      0      0    30%   9-22
backend\app\services\knowledge\version_service.py                    25     16      2      0    33%   13-36, 45-53, 59-60
backend\app\services\llm\gemini_service.py                           82     58     14      0    25%   34-40, 45-51, 54, 58-59, 63-67, 71-73, 76, 79-86, 90, 98-162
backend\app\services\llm\intent_router.py                           107     28     56     18    67%   53, 68-72, 76-78, 82, 86-89, 101, 106, 111, 115, 125, 134, 143, 147, 155, 167, 179->197, 184-185, 193-194, 221-222
backend\app\services\llm\response_formatter.py                       50     46     24      0     5%   6-19, 28-37, 44-109
backend\app\services\planner_service.py                              90     73     44      0    13%   13, 17, 22-51, 55-117, 121-142, 146-165, 171-172, 176-178, 182-183, 187-188, 192-193
backend\app\services\rag\chunking_service.py                          4      1      0      0    75%   10
backend\app\services\rag\debug_logger.py                             73     53      4      0    26%   24-75, 79, 136-195, 202, 206-208
backend\app\services\rag\dynamic_indexer.py                         162    140     38      0    11%   23-25, 32-42, 49-82, 94-202, 247-300, 307-387
backend\app\services\rag\query_normalizer.py                         53     45     30      0    10%   30-81, 94-124
backend\app\services\rag\rag_service.py                             196    185    122      0     3%   19-49, 53-326, 339-419
backend\app\services\rag\retriever.py                               629    593    318      0     4%   25-58, 63-105, 110-114, 121-123, 132, 137, 145-155, 160, 168-215, 219-238, 258-262, 265-402, 407-423, 431-536, 546-1179
backend\app\services\rag\vector_store.py                              9      1      0      0    89%   20
backend\app\services\timeline_service.py                             84     70     30      0    12%   11-12, 16, 25-27, 37-197, 201-208, 213
backend\app\services\timetable_import_service.py                     58     47     20      0    14%   19-136
backend\app\services\timetable_service.py                           181    159     70      0     9%   16, 20-28, 43-65, 75, 81-92, 98-119, 125-171, 183-251, 257-280, 287-325, 335-344, 350-359, 365-377, 383-398, 404-416
backend\app\services\websites\content_normalizer.py                  59      1     24      7    90%   56, 71->110, 73->85, 85->92, 92->99, 99->106, 106->110
backend\app\services\websites\crawler.py                             11      6      2      0    38%   12-19
backend\app\services\websites\extractor.py                          104     97     58      0     4%   18-172
backend\app\services\websites\metadata.py                            37     32     20      0     9%   9-63, 69-72
backend\app\services\websites\pipeline.py                            84     67     20      0    16%   27-191
backend\app\services\websites\scheduler.py                           75     52     14      0    26%   26-32, 43-54, 62-74, 81-104, 127-149, 154, 157, 160
backend\app\services\websites\scraper.py                             60     50     16      0    13%   13-15, 19-150, 157-161
backend\app\services\websites\validator.py                           31     27     14      0     9%   8-24, 31-48
backend\app\services\websites\website_service.py                    219    203     62      0     6%   14-15, 21-27, 33-38, 46-124, 131-149, 156-381, 387-431, 443-457, 463-494
backend\app\student\repository.py                                    49     34      6      0    27%   7, 14-17, 23-28, 34, 40, 46-55, 61-63, 69-70, 76, 82, 94-103
backend\app\student\routes.py                                        53     25      4      0    49%   29, 42, 53-54, 65-67, 100, 127-128, 147-148, 160-161, 173-182, 214-221
backend\app\student\schemas.py                                       73     16      8      0    70%   20-23, 50-53, 76-79, 84-87
backend\app\student\service.py                                      137    114     46      0    13%   18, 25-70, 74, 80-87, 93-118, 124-175, 203, 218-253, 265-274, 280-324, 330-341, 362-369
backend\app\student\validators.py                                    18      9      4      0    41%   16-31, 37-39
backend\app\student_preferences\models.py                            15      9      0      0    40%   15-31, 37
backend\app\student_preferences\repository.py                        19     10      0      0    47%   7, 13, 19-22, 28-32, 38-39
backend\app\student_preferences\routes.py                            25      9      0      0    64%   23, 33-34, 45-46, 57-58, 68-69
backend\app\student_preferences\schemas.py                           94     40     24      0    46%   39-42, 47-50, 55-58, 63-66, 81-86, 91-96, 101-106, 111-116
backend\app\student_preferences\service.py                           61     48     28      0    15%   14, 20-24, 31-36, 47-64, 74-110, 117-130
backend\app\utils\loader.py                                           8      0      0      0   100%
-------------------------------------------------------------------------------------------------------------
TOTAL                                                             11070   7256   3238    120    28%
===================== 10 passed, 98 deselected in 44.77s ======================

```
