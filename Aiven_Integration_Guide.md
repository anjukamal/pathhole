# Aiven MySQL Integration Guide

Now that the application has been updated to use a cloud database instead of a local SQLite file, you must provision a free MySQL database on Aiven and set its connection URL as an Environment Variable in Vercel.

## 1. Create a Free MySQL Database on Aiven

1. Log in to your [Aiven Console](https://console.aiven.io/).
2. Click **Create service**.
3. Select **MySQL** as the service type.
4. Select the **Free plan** (available in select regions like AWS `eu-central-1` or `us-east-1`).
5. Wait for the database service to build (it may take a couple of minutes).
6. Once built, click on the **Service URI** to copy the secure connection string.
   - It will look something like this: `mysql://avnadmin:password@host:port/defaultdb?ssl-mode=REQUIRED`

## 2. Set the Environment Variable in Vercel

1. Log in to your [Vercel Dashboard](https://vercel.com/dashboard) and go to your `pathhole` project.
2. Click on **Settings** in the top navigation bar.
3. Click on **Environment Variables** in the left sidebar.
4. Add a new variable with the following details:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the exact Aiven Service URI you copied from Step 1.
5. Click **Save**.

## 3. Redeploy your Project

Since you changed both the Environment Variables and the application code (which I just pushed to GitHub for you), Vercel needs to redeploy.

1. In Vercel, go to the **Deployments** tab.
2. Click **Redeploy** on the latest push, or simply push a new commit to GitHub to trigger it automatically.

Once the new deployment finishes, your `500 INTERNAL_SERVER_ERROR` will be fully resolved and your app will be online!
