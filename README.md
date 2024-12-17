# Agent Swarm Implementation

## Overview
This project implements a distributed AI agent system using a simplified, container-based architecture. The design emphasizes practical implementation over theoretical perfection, following the principle "as simple as possible, but no simpler."

## Architecture
Based on [AgentSwarm_Agents.txt](AgentSwarm_Agents.txt), the system uses a shallow hierarchy with:
- **Jarvis** as the primary orchestrator
- **Memory Agent** for data management
- **Task-specific agents** for specialized functions

## Core Components

### 1. Essential Services
As outlined in [AgentSwarm_Services.txt](AgentSwarm_Services.txt), the MVP includes:
- PostgreSQL for structured data
- Vector DB (ChromaDB) for semantic search
- Basic message queue system
- Core infrastructure services

### 2. Communication System
Following [AgentSwarm_comms.txt](AgentSwarm_comms.txt), we implement:
- JSON-based message schema
- Direct API calls for synchronous operations
- Message queues for asynchronous tasks
- Basic security measures (JWT, API keys)

### 3. Task Management
Based on [AgentSwarm_TaskLifecycle.txt](AgentSwarm_TaskLifecycle.txt), implementing:
- Task creation and assignment
- Status tracking
- Basic resource management
- Result handling

## Implementation Plan

### Phase 1: Infrastructure Setup
1. Docker container configuration
2. Database initialization
3. Message queue setup
4. Basic security implementation

### Phase 2: Memory Agent
1. PostgreSQL schema design
2. Vector DB integration
3. Basic API endpoints
4. Data management functions

### Phase 3: Orchestrator (Jarvis)
1. Core orchestration logic
2. Task management system
3. Agent communication handlers
4. Basic security integration

### Phase 4: First Task Agent
1. Implementation of one task agent (The Sage)
2. Full communication flow testing
3. Task lifecycle validation
4. Memory integration verification

## Deferred Features
To maintain simplicity, these features are postponed:
- Complex voice interfaces
- Advanced scaling capabilities
- Sophisticated memory consolidation
- Detailed monitoring systems

## Getting Started
(To be added during implementation)

## Contributing
(To be added during implementation)

## License
(To be added during implementation)

## Google API Setup

### Prerequisites
1. A Google Cloud Platform (GCP) account
2. A GCP project with the following APIs enabled:
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Tasks API
   - Google People API
   - Google Sheets API
   - Google Slides API

### Setup Instructions

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Note your Project ID for later use

2. **Enable Required APIs**:
   - In the Google Cloud Console, go to "APIs & Services" > "Library"
   - Search for and enable each API listed in the prerequisites
   - Wait for each API to be enabled before proceeding

3. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop application" as the application type
   - Name your OAuth 2.0 client
   - Download the client secret JSON file

4. **Configure Environment Variables**:
   - Create a `.env` file in the root directory (if not exists)
   - Add the following variables:
     ```
     GOOGLE_CREDENTIALS_FILE=path/to/your/client_secret.json
     GOOGLE_CLIENT_SECRET_FILE=path/to/your/client_secret.json
     ```
   - Replace `path/to/your/client_secret.json` with the actual path to your downloaded client secret file
   - Keep the client secret file outside the repository for security

5. **First-Time Authentication**:
   - Run the application
   - A browser window will open requesting authorization
   - Log in with your Google account
   - Grant the requested permissions
   - The application will save the authentication token for future use

### Security Notes
- Never commit the client secret file to version control
- Keep your `.env` file private and never commit it
- Regularly rotate your credentials for security
- Review and revoke access in your Google Account settings if needed

### Troubleshooting
- If you encounter authentication errors, delete the `token.pickle` file and re-authenticate
- Ensure all required APIs are enabled in your Google Cloud Console
- Check that your OAuth consent screen is properly configured
- Verify your client secret file path in the `.env` file is correct
