# Intelligent Document Processing (IDP) System

## Project Overview

This project is a serverless Intelligent Document Processing (IDP) application built on AWS. It demonstrates an event-driven architecture designed to ingest, process, validate, and persist invoice data automatically.

The system allows users to upload invoice documents (images/PDFs) via a frontend web application. These uploads trigger an asynchronous processing workflow that simulates data extraction (using Amazon Textract concepts), validates the business logic (e.g., checking for high-value invoices), and stores the results in a NoSQL database.

## Architecture

The system utilizes an event-driven microservices architecture powered by AWS CDK:

1. **Ingestion**: A user uploads an invoice to an **Amazon S3** bucket via the frontend (using a pre-signed URL).
2. **Processing**: An **S3 Event Notification** triggers the **Processor Lambda**. This function simulates the extraction of data (Vendor, Total Amount) from the document (mimicking Amazon Textract).
3. **Fanout**: Extracted data is published to an **Amazon SNS Topic** (`InvoiceEventsTopic`), enabling a decoupled fanout pattern.
4. **Persistence**: The **Persistor Lambda** subscribes to the SNS topic and saves the structured invoice data into **Amazon DynamoDB**.
5. **Validation**: The **Validator Lambda** also subscribes to the SNS topic. It checks if the invoice total exceeds a configured threshold ($1,000.00). If so, it publishes an alert to a separate **Alerts SNS Topic**.
6. **API Layer**: An **API Gateway** backed by a Lambda function serves the frontend, providing endpoints to fetch invoice lists and generate secure upload URLs.

## Technology Stack

- **Infrastructure as Code**: AWS CDK (TypeScript)
- **Backend Runtime**: Python 3.12 (AWS Lambda)
- **Frontend**: Vue.js 3, TypeScript, Vite
- **Storage & Messaging**: Amazon S3, Amazon DynamoDB, Amazon SNS
- **Package Manager**: Yarn

## Prerequisites

Before deploying, ensure you have the following installed:

- **Node.js** (v18 or later)
- **Yarn** (v1.x or v3.x)
- **AWS CLI** (Configured with `aws configure`)
- **Docker** (Required for bundling Python Lambda assets via CDK)
- **Python 3.12** (For local development of Lambda functions)

## Setup and Deployment

### 1. Clone and Install Dependencies

Clone the repository and install the project dependencies at the root level.
```bash
git clone <repository-url>
cd idp-project
yarn install
```

### 2. Deploy the Infrastructure

Use the AWS CDK to deploy the backend infrastructure.
```bash
# Bootstrap CDK (only required once per AWS account/region)
yarn cdk bootstrap

# Deploy the stack
yarn cdk deploy
```

**Important**: During deployment, you will see a list of Outputs in your terminal. Copy the value of `IdpInfrastructureStack.ApiUrl` (e.g., `https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/`). You will need this for the frontend configuration.

### 3. Configure the Frontend

Navigate to the frontend directory and configure the environment variables.
```bash
cd frontend
touch .env
```

Open `.env` and add the API URL you copied in the previous step:
```
VITE_API_BASE_URL='https://<your-api-id>.execute-api.<region>.amazonaws.com/prod/'
```

### 4. Run the Frontend Application

Install the frontend dependencies and start the local development server.
```bash
yarn install
yarn dev
```

Open your browser to the local URL provided (usually `http://localhost:5173`).

## Usage

1. **Upload**: Click "Upload Invoice" on the frontend and select an image or PDF.

2. **Processing**: The file is uploaded directly to S3 and the backend processes the file asynchronously.

   **Simulation Mode**: The current Processor Lambda is set to "Simulation Mode":
   - Files containing "high" in the name (e.g., `invoice-high.jpg`) will simulate a value > $1,000
   - Files containing "low" in the name will simulate a value of $50
   - Other files will generate a random value

3. **View Results**: Wait a few seconds and click "Refresh List" (or wait for the auto-refresh). The new invoice should appear in the table.

4. **Alerts**: If you uploaded a "high" value invoice, check the email address you configured in `lib/idp-stack.ts` for an SNS alert notification (ensure you have confirmed the AWS subscription email first).

## Project Structure

- `bin/` - Entry point for the CDK application
- `lib/` - Defines the AWS infrastructure stack (S3, DynamoDB, Lambdas, etc.)
- `lambda/` - Python source code for the microservices
  - `processor/` - Handles S3 events and data extraction
  - `persistor/` - Writes data to DynamoDB
  - `validator/` - Evaluates business rules and sends alerts
  - `api/` - Handles API Gateway requests
- `frontend/` - Vue.js web application

## Clean Up

To avoid incurring future charges, you can destroy the AWS resources created by this project:
```bash
yarn cdk destroy
```