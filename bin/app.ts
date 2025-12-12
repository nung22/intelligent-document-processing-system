#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { IdpInfrastructureStack } from '../lib/idp-stack';

const app = new cdk.App();
new IdpInfrastructureStack(app, 'IdpInfrastructureStack', {
  // Use the account and region configured in your AWS CLI
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});