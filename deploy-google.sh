#!/usr/bin/env bash
# Deploy Supreme Food Industry to Google Cloud Run (free tier eligible)
# Result URL example: https://supreme-food-industry-xxxxx-as.a.run.app
# Optional Firebase Hosting: https://supremefoodindustries.web.app
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-supremefoodindustries}"
REGION="${REGION:-asia-south1}"
SERVICE="supreme-food-industry"

echo "Using project: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

gcloud run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars "FLASK_DEBUG=0,SFI_SECRET=$(openssl rand -hex 16),SFI_ADMIN_PASSWORD=supreme@2000@" \
  --max-instances 3 \
  --memory 512Mi

echo ""
echo "Done. Open the Service URL printed above."
echo "Admin login: 9841043864 or 9840067681 / supreme@2000@"
echo ""
echo "Optional custom Google URL via Firebase Hosting:"
echo "  npm i -g firebase-tools"
echo "  firebase login"
echo "  firebase use $PROJECT_ID"
echo "  firebase hosting:channel:deploy live"
echo "  → https://$PROJECT_ID.web.app"
