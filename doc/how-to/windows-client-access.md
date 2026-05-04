# Windows Client Access Guide (How-to)

This guide provides step-by-step instructions for configuring Windows 10 and 11 client computers to access the **Migasfree Console (migasfree-frontend)** and other administration interfaces securely.

## 1. Local Host Mapping (DNS)

When running Migasfree in a local testing or development environment without a corporate DNS server, Windows clients need local hostname resolution.

To map the Migasfree domain to the Swarm manager's IP on a Windows client:

1. Click the **Start** button, type `Notepad`, and right-click it to select **Run as administrator**.
2. Go to **File** > **Open** and navigate to:
   `C:\Windows\System32\drivers\etc`
3. Change the file type dropdown from *Text Documents (\*.txt)* to *All Files (\*.\*)*.
4. Select the `hosts` file and click **Open**.
5. Add your server mapping at the bottom of the file (replace `192.168.1.100` with the actual Swarm manager IP and `acme.com` with your FQDN):

   ```text
   192.168.1.100 migasfree.acme.com
   192.168.1.100 portainer-migasfree.acme.com
   192.168.1.100 database-migasfree.acme.com
   192.168.1.100 datashare-migasfree.acme.com
   192.168.1.100 datastore-migasfree.acme.com
   192.168.1.100 worker-migasfree.acme.com
   ```

6. Save the file and close Notepad.

---

## 2. Managing SSL Certificate Warnings on Windows

If your Migasfree Swarm deployment uses self-signed certificates (such as in local testing environments), you will encounter security warnings in your browser. To resolve this, install the Migasfree CA certificate on the Windows machine.

### Importing the Root CA to the Windows Certificate Store

1. Retrieve the Migasfree Root CA certificate (`ca.crt` or `.pem`) from the shared storage or Datashare Console (`certificates/` volume).
2. On your Windows client, right-click the certificate file and select **Install Certificate** (or **Install PFX**).
3. In the **Certificate Import Wizard**, select **Local Machine** as the store location and click **Next**.
4. Grant administrator permission if prompted.
5. Choose **Place all certificates in the following store** and click **Browse**.
6. Select **Trusted Root Certification Authorities** from the list and click **OK**.
7. Click **Next** and then **Finish**.

> [!NOTE]
> Once imported, browsers like Microsoft Edge and Google Chrome on the Windows client will trust your self-signed Migasfree certificate automatically, eliminating the security warnings.

---

## 3. Mutual TLS (mTLS) for Windows Administrators

If **mTLS** is enabled (`MTLS = 'True'` in `env.py`), your browser on Windows must present a valid client certificate to access the console.

### Installing a Client Certificate on Windows

1. Generate your administrative certificate via the command:

   ```bash
   ./migasfree-swarm url-admin-certificate
   ```

2. Navigate to the returned one-time URL and download the `.p12` (PKCS#12) certificate file.
3. On Windows 10/11, double-click the `.p12` file to launch the **Certificate Import Wizard**.
4. Set the Store Location to **Current User** and click **Next**.
5. Confirm the file path and click **Next**.
6. Type the certificate password (if any) and leave the other options at their default values.
7. Let Windows automatically select the certificate store (it goes into **Personal**) or select it manually.
8. Click **Next** and **Finish**.

Now, when navigating to `https://<YOUR_FQDN>/`, your browser will prompt you to select your installed certificate. Choose your newly imported certificate to log into the **Migasfree Console**.

---

## 4. Allowing Windows Clients on the Subnet

To access the administrative consoles from a Windows client located on another subnet, update your access control permissions.

Edit the `env.py` file on your manager node to add your Windows client subnet to the `NETWORK_MNG` variable:

```python
# env.py
NETWORK_MNG = '192.168.1.0/24'  # Allow Windows client network access
```

Apply the changes by redeploying the service:

```bash
./migasfree-swarm deploy
```
