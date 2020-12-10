# helper script to get started with google cloud run
# prerequisites:
# - set PROJECT_ID=[your project ID] and REGION=[your region]
# - create a SQL instance
gcloud sql instances create {{ cookiecutter.project_slug }}_instance --project $PROJECT_ID --database-version POSTGRES_11 --tier db-f1-micro --region $REGION
# create database
gcloud sql databases create {{cookiecutter.project_slug}}_db --instance {{ cookiecutter.project_slug }}_instance
# create bucket for static files
gsutil mb gs://{{cookiecutter.project_slug}}-media
# set up secrets in secret manager
gcloud secrets create {{cookiecutter.project_slug}}_settings --replication-policy automatic
# (create .env.production file here)
gcloud secrets versions add {{cookiecutter.project_slug}}_settings --data-file .env.production
gcloud secrets add-iam-policy-binding {{cookiecutter.project_slug}}_settings  --member serviceAccount:${CLOUDRUN} --role roles/secretmanager.secretAccessor
export PROJECTNUM=$(gcloud projects describe ${PROJECT_ID} --format 'value(projectNumber)')
export CLOUDBUILD=${PROJECTNUM}@cloudbuild.gserviceaccount.com
gcloud secrets add-iam-policy-binding {{cookiecutter.project_slug}}_settings  --member serviceAccount:${CLOUDBUILD} --role roles/secretmanager.secretAccessor
gcloud projects add-iam-policy-binding ${PROJECT_ID}  --member serviceAccount:${CLOUDBUILD} --role roles/cloudsql.client
gcloud builds submit --config cloudmigrate.yaml  --substitutions _REGION=$REGION
gcloud run deploy {{cookiecutter.project_slug|replace('_', '-')}}-project --platform managed --region $REGION --image gcr.io/$PROJECT_ID/{{cookiecutter.project_slug}}-cloudrun --add-cloudsql-instances ${PROJECT_ID}:${REGION}:{{ cookiecutter.project_slug }}_instance  --allow-unauthenticated --set-env-vars=DJANGO_SETTINGS_MODULE={{cookiecutter.project_slug}}.settings_google
