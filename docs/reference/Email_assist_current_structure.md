Email_assist_current/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── main.py
├── config.py
├── prompts.py
├── AgentSwarmPlan.txt
├── AgentSwarm_TaskLifecycle.txt
├── AgentSwarm_Tools.txt
├── AgentSwarm_comms.txt
├── AgentSwarm_Services.txt
├── AgentSwarm_Agents.txt
├── AgentPlan.txt
├── CursorRules_AddaTool.md
├── migrate_database.py
├── verify_user_state.py
├── set_user_info.py
├── migrate_user_details.py
├── test_simple_rag.py
├── simple_rag.py
├── test_document_processing.py
├── document_cli.py
├── check_docs.py
├── test_db_connection.py
├── test_google_api.py
├── terminalstyle.py
├── n8n_workflow.json
├── SearXNG_api.txt
├── people_rest.json

├── src/
│   └── __init__.py

├── tools/
│   ├── __init__.py
│   ├── api_builder.py
│   ├── credentials_handler.py
│   ├── file_tools.py
│   ├── google_api_tools.py
│   ├── google_calendar_tools.py
│   ├── google_drive_tools.py
│   ├── google_mail_tools.py
│   ├── google_people_tools.py
│   ├── google_sheets_tools.py
│   ├── google_slides_tools.py
│   ├── google_tasks_tools.py
│   ├── llm_config.py
│   ├── llm_tools.py
│   ├── new__init__.py
│   ├── new_credentials_handler.py
│   ├── new_tool_handler.py
│   ├── perplexity_api_tools.py
│   ├── rag_tools.py
│   ├── searxng_tools.py
│   ├── smtp_mail_tools_OpenWebUI.py
│   ├── time_tools.py
│   ├── tool_definitions.py
│   ├── tool_handler.py
│   ├── tool_registry.py
│   ├── universal_tool_handler.py
│   └── user_state.py

├── services/
│   └── document_tools.py

├── tests/
│   ├── test_simple_rag.py
│   ├── test_document_processing.py
│   ├── test_db_connection.py
│   └── test_google_api.py

├── data/
│   └── (data files)

├── Docs/
│   └── (documentation files)

├── agent_directory/
│   ├── AgencySwarmREADME.md
│   └── Tool_Creation_Link_ReadMe.md

├── OpenAIDocs/
│   └── (OpenAI documentation)

└── .vscode/
    └── (VS Code settings)
```

Key File Descriptions:

1. Core Configuration Files:
```markdown
.env                    - Environment variables and configuration
.gitignore             - Git ignore patterns
README.md              - Project documentation
requirements.txt       - Python dependencies
config.py             - Application configuration
main.py               - Main application entry point
```

2. Agent and Planning Documentation:
```markdown
AgentSwarmPlan.txt           - Overall swarm architecture plan
AgentSwarm_TaskLifecycle.txt - Task lifecycle documentation
AgentSwarm_Tools.txt         - Tools documentation
AgentSwarm_comms.txt         - Communication protocols
AgentSwarm_Services.txt      - Services documentation
AgentSwarm_Agents.txt        - Agent definitions
AgentPlan.txt               - Agent planning documentation
```

3. Tool Implementation Files:
```markdown
tools/
├── api_builder.py              - API construction utilities
├── credentials_handler.py      - Credential management
├── file_tools.py              - File operations
├── google_api_tools.py        - Google API core functionality
├── google_calendar_tools.py   - Calendar operations
├── google_drive_tools.py      - Drive operations
├── google_mail_tools.py       - Gmail operations
├── google_people_tools.py     - People API operations
├── google_sheets_tools.py     - Sheets operations
├── google_slides_tools.py     - Slides operations
├── google_tasks_tools.py      - Tasks operations
├── llm_tools.py              - Language model utilities
├── rag_tools.py              - Retrieval-augmented generation
├── searxng_tools.py          - Search operations
├── time_tools.py             - Time utilities
├── tool_definitions.py        - Tool definitions
├── tool_handler.py           - Tool execution handling
└── tool_registry.py          - Tool registration system
```

4. Testing Files:
```markdown
tests/
├── test_simple_rag.py          - RAG testing
├── test_document_processing.py - Document processing tests
├── test_db_connection.py       - Database connection tests
└── test_google_api.py         - Google API tests
```

5. Service Files:
```markdown
services/
└── document_tools.py          - Document processing services
``` 