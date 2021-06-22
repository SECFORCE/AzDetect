###### Author: @ptrac3
###### Most of the email code logic is taken from https://www.geeksforgeeks.org/python-fetch-your-gmail-emails-from-a-particular-user/
###### Please only use the following code for PoC purposes only and at your own risk
###### Ensure that the AZ CLI tools are correctly configured before running this tool: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Imports and requirements
import imaplib, email, quopri, codecs
from bs4 import BeautifulSoup as bs
import mailparser
import json
import ast
import subprocess
import os

##################
# Email Settings #
##################

# user = username
# password = password
# imap_url = mail server

user = ''
password = ''
imap_url = ''

#############################################
###    Custom functions to resolve an       #
### Azure Built-in Role to/from an id/name. #
#############################################
### Examples:
# - From ID to Name: print(get_azure_role_from_id('8e3af657-a8ff-443c-a75c-2fe8c4bcb635'))
# - From Name to ID: print(get_azure_role_id_from_name('Owner'))

# Azure Built-in roles lookup dictionary
azure_built_in_roles_lookup_dict_by_id = {'8311e382-0749-4cb8-b61a-304f252e45ec': 'AcrPush', '312a565d-c81f-4fd8-895a-4e21e48d571c': 'API Management Service Contributor', '7f951dda-4ed3-4680-a7ca-43fe172d538d': 'AcrPull', '6cef56e8-d556-48e5-a04f-b8e64114680f': 'AcrImageSigner', 'c2f4ef07-c644-48eb-af81-4b1b4947fb11': 'AcrDelete', 'cdda3590-29a3-44f6-95f2-9f980659eb04': 'AcrQuarantineReader', 'c8d4ff99-41c3-41a8-9f60-21dfdad59608': 'AcrQuarantineWriter', 'e022efe7-f5ba-4159-bbe4-b44f577e9b61': 'API Management Service Operator Role', '71522526-b88f-4d52-b57f-d31fc3546d0d': 'API Management Service Reader Role', 'ae349356-3a1b-4a5e-921d-050484c6347e': 'Application Insights Component Contributor', '08954f03-6346-4c2e-81c0-ec3a5cfae23b': 'Application Insights Snapshot Debugger', 'fd1bd22b-8476-40bc-a0bc-69b95687b9f3': 'Attestation Reader', '4fe576fe-1146-4730-92eb-48519fa6bf9f': 'Automation Job Operator', '5fb5aef8-1081-4b8e-bb16-9d5d0385bab5': 'Automation Runbook Operator', 'd3881f73-407a-4167-8283-e981cbba0404': 'Automation Operator', '4f8fab4f-1852-4a58-a46a-8eaf358af14a': 'Avere Contributor', 'c025889f-8102-4ebf-b32c-fc0c6f0c6bd9': 'Avere Operator', '0ab0b1a8-8aac-4efd-b8c2-3ee1fb270be8': 'Azure Kubernetes Service Cluster Admin Role', '4abbcc35-e782-43d8-92c5-2d3f1bd2253f': 'Azure Kubernetes Service Cluster User Role', '423170ca-a8f6-4b0f-8487-9e4eb8f49bfa': 'Azure Maps Data Reader', '6f12a6df-dd06-4f3e-bcb1-ce8be600526a': 'Azure Stack Registration Owner', '5e467623-bb1f-42f4-a55d-6e525e11384b': 'Backup Contributor', 'fa23ad8b-c56e-40d8-ac0c-ce449e1d2c64': 'Billing Reader', '00c29273-979b-4161-815c-10b084fb9324': 'Backup Operator', 'a795c7a0-d4a2-40c1-ae25-d81f01202912': 'Backup Reader', '31a002a1-acaf-453e-8a5b-297c9ca1ea24': 'Blockchain Member Node Access (Preview)', '5e3c6656-6cfa-4708-81fe-0de47ac73342': 'BizTalk Contributor', '426e0c7f-0c7e-4658-b36f-ff54d6c29b45': 'CDN Endpoint Contributor', '871e35f6-b5c1-49cc-a043-bde969a0f2cd': 'CDN Endpoint Reader', 'ec156ff8-a8d1-4d15-830c-5b80698ca432': 'CDN Profile Contributor', '8f96442b-4075-438f-813d-ad51ab4019af': 'CDN Profile Reader', 'b34d265f-36f7-4a0d-a4d4-e158ca92e90f': 'Classic Network Contributor', '86e8f5dc-a6e9-4c67-9d15-de283e8eac25': 'Classic Storage Account Contributor', '985d6b00-f706-48f5-a6fe-d0ca12fb668d': 'Classic Storage Account Key Operator Service Role', '9106cda0-8a86-4e81-b686-29a22c54effe': 'ClearDB MySQL DB Contributor', 'd73bb868-a0df-4d4d-bd69-98a00b01fccb': 'Classic Virtual Machine Contributor', 'a97b65f3-24c7-4388-baec-2e87135dc908': 'Cognitive Services User', 'b59867f0-fa02-499b-be73-45a86b5b3e1c': 'Cognitive Services Data Reader (Preview)', '25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68': 'Cognitive Services Contributor', 'db7b14f2-5adf-42da-9f96-f2ee17bab5cb': 'CosmosBackupOperator', 'b24988ac-6180-42a0-ab88-20f7382dd24c': 'Contributor', 'fbdf93bf-df7d-467e-a4d2-9458aa1360c8': 'Cosmos DB Account Reader Role', '434105ed-43f6-45c7-a02f-909b2ba83430': 'Cost Management Contributor', '72fafb9e-0641-4937-9268-a91bfd8191a3': 'Cost Management Reader', 'add466c9-e687-43fc-8d98-dfcf8d720be5': 'Data Box Contributor', '028f4ed7-e2a9-465e-a8f4-9c0ffdfdc027': 'Data Box Reader', '673868aa-7521-48a0-acc6-0f60742d39f5': 'Data Factory Contributor', '150f5e0c-0603-4f03-8c7f-cf70034c4e90': 'Data Purger', '47b7735b-770e-4598-a7da-8b91488b4c88': 'Data Lake Analytics Developer', '76283e04-6283-4c54-8f91-bcf1374a3c64': 'DevTest Labs User', '5bd9cd88-fe45-4216-938b-f97437e15450': 'DocumentDB Account Contributor', 'befefa01-2a29-4197-83a8-272ff33ce314': 'DNS Zone Contributor', '428e0ff0-5e57-4d9c-a221-2c70d0e0a443': 'EventGrid EventSubscription Contributor', '2414bbcf-6497-4faf-8c65-045460748405': 'EventGrid EventSubscription Reader', 'b60367af-1334-4454-b71e-769d9a4f83d9': 'Graph Owner', '8d8d5a11-05d3-4bda-a417-a08778121c7c': 'HDInsight Domain Services Contributor', '03a6d094-3444-4b3d-88af-7477090a9e5e': 'Intelligent Systems Account Contributor', 'f25e0fa2-a7c8-4377-a976-54943a77a395': 'Key Vault Contributor', 'ee361c5d-f7b5-4119-b4b6-892157c8f64c': 'Knowledge Consumer', 'b97fb8bc-a8b2-4522-a38b-dd33c7e65ead': 'Lab Creator', '73c42c96-874c-492b-b04d-ab87d138a893': 'Log Analytics Reader', '92aaf0da-9dab-42b6-94a3-d43ce8d16293': 'Log Analytics Contributor', '515c2055-d9d4-4321-b1b9-bd0c9a0f79fe': 'Logic App Operator', '87a39d53-fc1b-424a-814c-f7e04687dc9e': 'Logic App Contributor', 'c7393b34-138c-406f-901b-d8cf2b17e6ae': 'Managed Application Operator Role', 'b9331d33-8a36-4f8c-b097-4f54124fdb44': 'Managed Applications Reader', 'f1a07417-d97a-45cb-824c-7a7467783830': 'Managed Identity Operator', 'e40ec5ca-96e0-45a2-b4ff-59039f2c2b59': 'Managed Identity Contributor', '5d58bcaf-24a5-4b20-bdb6-eed9f69fbe4c': 'Management Group Contributor', 'ac63b705-f282-497d-ac71-919bf39d939d': 'Management Group Reader', '3913510d-42f4-4e42-8a64-420c390055eb': 'Monitoring Metrics Publisher', '43d0d8ad-25c7-4714-9337-8ba259a9fe05': 'Monitoring Reader', '4d97b98b-1d4f-4787-a291-c67834d212e7': 'Network Contributor', '749f88d5-cbae-40b8-bcfc-e573ddc772fa': 'Monitoring Contributor', '5d28c62d-5b37-4476-8438-e587778df237': 'New Relic APM Account Contributor', '8e3af657-a8ff-443c-a75c-2fe8c4bcb635': 'Owner', 'acdd72a7-3385-48ef-bd42-f606fba81ae7': 'Reader', 'e0f68234-74aa-48ed-b826-c38b57376e17': 'Redis Cache Contributor', 'c12c1c16-33a1-487b-954d-41c89c60f349': 'Reader and Data Access', '36243c78-bf99-498c-9df9-86d9f8d28608': 'Resource Policy Contributor', '188a0f2f-5c9e-469b-ae67-2aa5ce574b94': 'Scheduler Job Collections Contributor', '7ca78c08-252a-4471-8644-bb5ff32d4ba0': 'Search Service Contributor', 'fb1c8493-542b-48eb-b624-b4c8fea62acd': 'Security Admin', 'e3d13bf0-dd5a-482e-ba6b-9b8433878d10': 'Security Manager (Legacy)', '39bc4728-0917-49c7-9d2c-d95423bc2eb4': 'Security Reader', '8bbe83f1-e2a6-4df7-8cb4-4e04d4e5c827': 'Spatial Anchors Account Contributor', '6670b86e-a3f7-4917-ac9b-5d6ab1be4567': 'Site Recovery Contributor', '494ae006-db33-4328-bf46-533a6560a3ca': 'Site Recovery Operator', '5d51204f-eb77-4b1c-b86a-2ec626c49413': 'Spatial Anchors Account Reader', 'dbaa88c4-0c30-4179-9fb3-46319faa6149': 'Site Recovery Reader', '70bbe301-9835-447d-afdd-19eb3167307c': 'Spatial Anchors Account Owner', '4939a1f6-9ae0-4e48-a1e0-f2cbe897382d': 'SQL Managed Instance Contributor', '9b7fa17d-e63e-47b0-bb0a-15c516ac86ec': 'SQL DB Contributor', '056cd41c-7e88-42e1-933e-88ba6a50c9c3': 'SQL Security Manager', '17d1049b-9a84-46fb-8f53-869881c3d3ab': 'Storage Account Contributor', '6d8ee4ec-f05a-4a1d-8b00-a9b17e38b437': 'SQL Server Contributor', '81a9662b-bebf-436f-a333-f67b29880f12': 'Storage Account Key Operator Service Role', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe': 'Storage Blob Data Contributor', 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b': 'Storage Blob Data Owner', '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1': 'Storage Blob Data Reader', '974c5e8b-45b9-4653-ba55-5f855dd0fb88': 'Storage Queue Data Contributor', '8a0f0c08-91a1-4084-bc3d-661d67233fed': 'Storage Queue Data Message Processor', 'c6a89b2d-59bc-44d0-9896-0f6e12d7b80a': 'Storage Queue Data Message Sender', '19e7f393-937e-4f77-808e-94535e297925': 'Storage Queue Data Reader', 'cfd33db0-3dd1-45e3-aa9d-cdbdf3b6f24e': 'Support Request Contributor', 'a4b10055-b0c7-44c2-b00f-c7b5b3550cf7': 'Traffic Manager Contributor', '1c0163c0-47e6-4577-8991-ea5c82e286e4': 'Virtual Machine Administrator Login', '18d7d88d-d35e-4fb5-a5c3-7773c20a72d9': 'User Access Administrator', 'fb879df8-f326-4884-b1cf-06f3ad86be52': 'Virtual Machine User Login', '9980e02c-c2be-4d73-94e8-173b1dc7cf3c': 'Virtual Machine Contributor', '2cc479cb-7b4d-49a8-b449-8c00fd0f0a4b': 'Web Plan Contributor', 'de139f84-1756-47ae-9be6-808fbbe84772': 'Website Contributor', '090c5cfd-751d-490a-894a-3ce6f1109419': 'Azure Service Bus Data Owner', 'f526a384-b230-433a-b45c-95f59c4a2dec': 'Azure Event Hubs Data Owner', 'bbf86eb8-f7b4-4cce-96e4-18cddf81d86e': 'Attestation Contributor', '61ed4efc-fab3-44fd-b111-e24485cc132a': 'HDInsight Cluster Operator', '230815da-be43-4aae-9cb4-875f7bd000aa': 'Cosmos DB Operator', '48b40c6e-82e0-4eb3-90d5-19e40f49b624': 'Hybrid Server Resource Administrator', '5d1e5ee4-7c68-4a71-ac8b-0739630a3dfb': 'Hybrid Server Onboarding', 'a638d3c7-ab3a-418d-83e6-5f17a39d4fde': 'Azure Event Hubs Data Receiver', '2b629674-e913-4c01-ae53-ef4638d8f975': 'Azure Event Hubs Data Sender', '4f6d3b9b-027b-4f4c-9142-0e5a2a2247e0': 'Azure Service Bus Data Receiver', '69a216fc-b8fb-44d8-bc22-1f3c2cd27a39': 'Azure Service Bus Data Sender', 'aba4ae5f-2193-4029-9191-0cb91df5e314': 'Storage File Data SMB Share Reader', '0c867c2a-1d8c-454a-a3db-ab2ea1bdc8bb': 'Storage File Data SMB Share Contributor', 'b12aa53e-6015-4669-85d0-8515ebb3ae7f': 'Private DNS Zone Contributor', 'db58b8e5-c6ad-4a2a-8342-4190687cbf4a': 'Storage Blob Delegator', '1d18fff3-a72a-46b5-b4a9-0b38a3cd7e63': 'Desktop Virtualization User', 'a7264617-510b-434b-a828-9731dc254ea7': 'Storage File Data SMB Share Elevated Contributor', '41077137-e803-4205-871c-5a86e6a753b4': 'Blueprint Contributor', '437d2ced-4a38-4302-8479-ed2bcb43d090': 'Blueprint Operator', 'ab8e14d6-4a74-4a29-9ba8-549422addade': 'Azure Sentinel Contributor', '3e150937-b8fe-4cfb-8069-0eaf05ecd056': 'Azure Sentinel Responder', '8d289c81-5878-46d4-8554-54e1e3d8b5cb': 'Azure Sentinel Reader', 'b279062a-9be3-42a0-92ae-8b3cf002ec4d': 'Workbook Reader', 'e8ddcd69-c73f-4f9f-9844-4100522f16ad': 'Workbook Contributor', '66bb4e9e-b016-4a94-8249-4c0511c2be84': 'Policy Insights Data Writer (Preview)', '04165923-9d83-45d5-8227-78b77b0a687e': 'SignalR AccessKey Reader', '8cf5e20a-e4b2-4e9d-b3a1-5ceb692c2761': 'SignalR Contributor', 'b64e21ea-ac4e-4cdf-9dc9-5b892992bee7': 'Azure Connected Machine Onboarding', 'cd570a14-e51a-42ad-bac8-bafd67325302': 'Azure Connected Machine Resource Administrator', '91c1777a-f3dc-4fae-b103-61d183457e46': 'Managed Services Registration assignment Delete Role', '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b': 'App Configuration Data Owner', '516239f1-63e1-4d78-a4de-a74fb236a071': 'App Configuration Data Reader', '34e09817-6cbe-4d01-b1a2-e0eac5743d41': 'Kubernetes Cluster - Azure Arc Onboarding', '7f646f1b-fa08-80eb-a22b-edd6ce5c915c': 'Experimentation Contributor', '466ccd10-b268-4a11-b098-b4849f024126': 'Cognitive Services QnA Maker Reader', 'f4cc2bf9-21be-47a1-bdf1-5c5804381025': 'Cognitive Services QnA Maker Editor', '7f646f1b-fa08-80eb-a33b-edd6ce5c915c': 'Experimentation Administrator', '3df8b902-2a6f-47c7-8cc5-360e9b272a7e': 'Remote Rendering Administrator', 'd39065c4-c120-43c9-ab0a-63eed9795f0a': 'Remote Rendering Client', '641177b8-a67a-45b9-a033-47bc880bb21e': 'Managed Application Contributor Role', '612c2aa1-cb24-443b-ac28-3ab7272de6f5': 'Security Assessment Contributor', '4a9ae827-6dc8-4573-8ac7-8239d42aa03f': 'Tag Contributor', 'c7aa55d3-1abb-444a-a5ca-5e51e485d6ec': 'Integration Service Environment Developer', 'a41e2c5b-bd99-4a07-88f4-9bf657a760b8': 'Integration Service Environment Contributor', 'ed7f3fbd-7b88-4dd4-9017-9adb7ce333f8': 'Azure Kubernetes Service Contributor Role', 'd57506d4-4c8d-48b1-8587-93c323f6a5a3': 'Azure Digital Twins Data Reader', 'bcd981a7-7f74-457b-83e1-cceb9e632ffe': 'Azure Digital Twins Data Owner', '350f8d15-c687-4448-8ae1-157740a3936d': 'Hierarchy Settings Administrator', '5a1fc7df-4bf1-4951-a576-89034ee01acd': 'FHIR Data Contributor', '3db33094-8700-4567-8da5-1501d4e7e843': 'FHIR Data Exporter', '4c8d0bbc-75d3-4935-991f-5f3c56d81508': 'FHIR Data Reader', '3f88fce4-5892-4214-ae73-ba5294559913': 'FHIR Data Writer', '49632ef5-d9ac-41f4-b8e7-bbe587fa74a1': 'Experimentation Reader', '4dd61c23-6743-42fe-a388-d8bdd41cb745': 'Object Understanding Account Owner', '8f5e0ce6-4f7b-4dcf-bddf-e6f48634a204': 'Azure Maps Data Contributor', 'c1ff6cc2-c111-46fe-8896-e0ef812ad9f3': 'Cognitive Services Custom Vision Contributor', '5c4089e1-6d96-4d2f-b296-c1bc7137275f': 'Cognitive Services Custom Vision Deployment', '88424f51-ebe7-446f-bc41-7fa16989e96c': 'Cognitive Services Custom Vision Labeler', '93586559-c37d-4a6b-ba08-b9f0940c2d73': 'Cognitive Services Custom Vision Reader', '0a5ae4ab-0d65-4eeb-be61-29fc9b54394b': 'Cognitive Services Custom Vision Trainer', '00482a5a-887f-4fb3-b363-3b7fe8e74483': 'Key Vault Administrator', '14b46e9e-c2b7-41b4-b07b-48a6ebf60603': 'Key Vault Crypto Officer', '12338af0-0e69-4776-bea7-57ae8d297424': 'Key Vault Crypto User', 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7': 'Key Vault Secrets Officer', '4633458b-17de-408a-b874-0445c86b69e6': 'Key Vault Secrets User', 'a4417e6f-fecd-4de8-b567-7b0420556985': 'Key Vault Certificates Officer', '21090545-7ca7-4776-b22c-e363652d74d2': 'Key Vault Reader', 'e147488a-f6f5-4113-8e2d-b22465e65bf6': 'Key Vault Crypto Service Encryption User', '63f0a09d-1495-4db4-a681-037d84835eb4': 'Azure Arc Kubernetes Viewer', '5b999177-9696-4545-85c7-50de3797e5a1': 'Azure Arc Kubernetes Writer', '8393591c-06b9-48a2-a542-1bd6b377f6a2': 'Azure Arc Kubernetes Cluster Admin', 'dffb1e0c-446f-4dde-a09f-99eb5cc68b96': 'Azure Arc Kubernetes Admin', 'b1ff04bb-8a4e-4dc4-8eb5-8693973ce19b': 'Azure Kubernetes Service RBAC Cluster Admin', '3498e952-d568-435e-9b2c-8d77e338d7f7': 'Azure Kubernetes Service RBAC Admin', '7f6c6a51-bcf8-42ba-9220-52d62157d7db': 'Azure Kubernetes Service RBAC Reader', 'a7ffa36f-339b-4b5c-8bdf-e2c188b2c0eb': 'Azure Kubernetes Service RBAC Writer', '82200a5b-e217-47a5-b665-6d8765ee745b': 'Services Hub Operator', 'd18777c0-1514-4662-8490-608db7d334b6': 'Object Understanding Account Reader', '00493d72-78f6-4148-b6c5-d3ce8e4799dd': 'Azure Arc Enabled Kubernetes Cluster User Role', '420fcaa2-552c-430f-98ca-3264be4806c7': 'SignalR App Server (Preview)', 'fd53cd77-2268-407a-8f46-7e7863d0f521': 'SignalR Serverless Contributor (Preview)', 'daa9e50b-21df-454c-94a6-a8050adab352': 'Collaborative Data Contributor', 'e9dba6fb-3d52-4cf0-bce3-f06ce71b9e0f': 'Device Update Reader', '02ca0879-e8e4-47a5-a61e-5c618b76e64a': 'Device Update Administrator', '0378884a-3af5-44ab-8323-f5b22f9f3c98': 'Device Update Content Administrator', 'e4237640-0e3d-4a46-8fda-70bc94856432': 'Device Update Deployments Administrator', '49e2f5d2-7741-4835-8efa-19e1fe35e47f': 'Device Update Deployments Reader', 'd1ee9a80-8b14-47f0-bdc2-f4a351625a7b': 'Device Update Content Reader', 'cb43c632-a144-4ec5-977c-e80c4affc34a': 'Cognitive Services Metrics Advisor Administrator', '3b20f47b-3825-43cb-8114-4bd2201156a8': 'Cognitive Services Metrics Advisor User', '2c56ea50-c6b3-40a6-83c0-9d98858bc7d2': 'Schema Registry Reader (Preview)', '5dffeca3-4936-4216-b2bc-10343a5abb25': 'Schema Registry Contributor (Preview)', '7ec7ccdc-f61e-41fe-9aaf-980df0a44eba': 'AgFood Platform Service Reader', '8508508a-4469-4e45-963b-2518ee0bb728': 'AgFood Platform Service Contributor', 'f8da80de-1ff9-4747-ad80-a19b7f6079e3': 'AgFood Platform Service Admin', '18500a29-7fe2-46b2-a342-b16a415e101d': 'Managed HSM contributor', '0b555d9b-b4a7-4f43-b330-627f0e5be8f0': 'Security Detonation Chamber Submitter', 'ddde6b66-c0df-4114-a159-3618637b3035': 'SignalR Service Reader (Preview)', '7e4f1700-ea5a-4f59-8f37-079cfe29dce3': 'SignalR Service Owner (Preview)', 'f7b75c60-3036-4b75-91c3-6b41c27c1689': 'Reservation Purchaser', '635dd51f-9968-44d3-b7fb-6d9a6bd613ae': 'AzureML Metrics Writer (preview)', 'e5e2a7ff-d759-4cd2-bb51-3152d37e2eb1': 'Storage Account Backup Contributor Role', '6188b7c9-7d01-4f99-a59f-c88b630326c0': 'Experimentation Metric Contributor', '9ef4ef9c-a049-46b0-82ab-dd8ac094c889': 'Project Babylon Data Curator', 'c8d896ba-346d-4f50-bc1d-7d1c84130446': 'Project Babylon Data Reader', '05b7651b-dc44-475e-b74d-df3db49fae0f': 'Project Babylon Data Source Administrator', '8a3c2885-9b38-4fd2-9d99-91af537c1347': 'Purview Data Curator', 'ff100721-1b9d-43d8-af52-42b69c1272db': 'Purview Data Reader', '200bba9e-f0c8-430f-892b-6f0794863803': 'Purview Data Source Administrator', 'ca6382a4-1721-4bcf-a114-ff0c70227b6b': 'Application Group Contributor', '49a72310-ab8d-41df-bbb0-79b649203868': 'Desktop Virtualization Reader', '082f0a83-3be5-4ba1-904c-961cca79b387': 'Desktop Virtualization Contributor', '21efdde3-836f-432b-bf3d-3e8e734d4b2b': 'Desktop Virtualization Workspace Contributor', 'ea4bfff8-7fb4-485a-aadd-d4129a0ffaa6': 'Desktop Virtualization User Session Operator', '2ad6aaab-ead9-4eaa-8ac5-da422f562408': 'Desktop Virtualization Session Host Operator', 'ceadfde2-b300-400a-ab7b-6143895aa822': 'Desktop Virtualization Host Pool Reader', 'e307426c-f9b6-4e81-87de-d99efb3c32bc': 'Desktop Virtualization Host Pool Contributor', 'aebf23d0-b568-4e86-b8f9-fe83a2c6ab55': 'Desktop Virtualization Application Group Reader', '86240b0e-9422-4c43-887b-b61143f32ba8': 'Desktop Virtualization Application Group Contributor', '0fa44ee9-7a7d-466b-9bb2-2bf446b1204d': 'Desktop Virtualization Workspace Reader', '3e5e47e6-65f7-47ef-90b5-e5dd4d455f24': 'Disk Backup Reader', 'b8b15564-4fa6-4a59-ab12-03e1d9594795': 'Autonomous Development Platform Data Contributor (Preview)', 'd63b75f7-47ea-4f27-92ac-e0d173aaf093': 'Autonomous Development Platform Data Reader (Preview)', '27f8b550-c507-4db9-86f2-f4b8e816d59d': 'Autonomous Development Platform Data Owner (Preview)', 'b50d9833-a0cb-478e-945f-707fcc997c13': 'Disk Restore Operator', '7efff54f-a5b4-42b5-a1c5-5411624893ce': 'Disk Snapshot Contributor', '5548b2cf-c94c-4228-90ba-30851930a12f': 'Microsoft.Kubernetes connected cluster role', 'a37b566d-3efa-4beb-a2f2-698963fa42ce': 'Security Detonation Chamber Submission Manager', '352470b3-6a9c-4686-b503-35deb827e500': 'Security Detonation Chamber Publisher', '7a6f0e70-c033-4fb1-828c-08514e5f4102': 'Collaborative Runtime Operator', '5432c526-bc82-444a-b7ba-57c5b0b5b34f': 'CosmosRestoreOperator', 'a1705bd2-3a8f-45a5-8683-466fcfd5cc24': 'FHIR Data Converter', 'f4c81013-99ee-4d62-a7ee-b3f1f648599a': 'Azure Sentinel Automation Contributor', '0e5f05e5-9ab9-446b-b98d-1e2157c94125': 'Quota Request Operator Role', '1e241071-0855-49ea-94dc-649edcd759de': 'EventGrid Contributor', '28241645-39f8-410b-ad48-87863e2951d5': 'Security Detonation Chamber Reader', '4a167cdf-cb95-4554-9203-2347fe489bd9': 'Object Anchors Account Reader', 'ca0835dd-bacc-42dd-8ed2-ed5e7230d15b': 'Object Anchors Account Owner', 'd17ce0a2-0697-43bc-aac5-9113337ab61c': 'WorkloadBuilder Migration Agent Role'}

def get_azure_role_from_id(role_id):
    return azure_built_in_roles_lookup_dict_by_id[role_id]
def get_azure_role_id_from_name(role_name):
    # Oneliner for getting a key from its value in a dictionary
    return list(azure_built_in_roles_lookup_dict_by_id.keys())[list(azure_built_in_roles_lookup_dict_by_id.values()).index(role_name)]
#######################################################################################

###### Custom Functions #######

# Function to detect if the account is an automation account
def isAutomationAccount(service_principal_id):
	try:
		homepage_value = subprocess.check_output("az ad sp show --id "+ service_principal_id+ "|jq -r '.homepage'", shell=True)
		return True
	except:
		return False

# Extract HTML from the RAW email
def extract_html(raw_email):
	content = str(raw_email[1], 'utf-8')
	data = str(content)
	# Parsing the email contents
	mail2 = mailparser.parse_from_string(content)
	# Extracting email body
	body = mail2.body
	# Parsing HTML with SOUP
	soup = bs(body,"html.parser")
	return soup
# Parse HTML with Beautifoul Soup
def parse_html(html_extracted_from_email):
	parsed_email_values = []
	for parsed_email_values_content in html_extracted_from_email.select('th[class*="small-12 large-8"]'):
		parsed_email_values.append(parsed_email_values_content.get_text())
	parsed_email_titles = []
	for parsed_email_titles_content in html_extracted_from_email.select('th[class*="small-12 large-4"]'):
		parsed_email_titles.append(parsed_email_titles_content.get_text())
	# Final Dictionary
	parsed_email = {parsed_email_titles[i].lower(): parsed_email_values[i] for i in range(len(parsed_email_titles))}
	return parsed_email

# Group of functions to resolve object_ids into user/group/service principal objects. Please note that this requires the 'az' tool already working and configured: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

def getUserPrincipalName(service_principal_id):
    userPrincipalName = subprocess.check_output("az ad user show --id "+ service_principal_id+ "|jq -r '.userPrincipalName'", shell=True).decode("utf-8").rstrip()
    return userPrincipalName
def getADGroupName(service_principal_id):
	get_group_command =  """az ad group list| jq .[]| jq 'select(.objectId=="%s")'| jq -r '.displayName'""" % (service_principal_id)
	group_name = subprocess.check_output(get_group_command, shell=True).decode("utf-8").rstrip()
	return group_name
def getServicePrincipalName(service_principal_id):
	service_principal_name = subprocess.check_output("az ad sp show --id "+ service_principal_id+ "|jq -r '.displayName'", shell=True).decode("utf-8").rstrip()
	return service_principal_name

# Function to get email content part i.e its body part 
def get_body(msg): 
    if msg.is_multipart(): 
        return get_body(msg.get_payload(0)) 
    else: 
        return msg.get_payload(None, True) 

# Function to search for a key value pair  
def search(key, value, con):  
    result, data = con.search(None, key, '"{}"'.format(value)) 
    return data 
  
# Function to get the list of emails under this label 
def get_emails(result_bytes): 
    msgs = [] # all the email data are pushed inside an array 
    for num in result_bytes[0].split(): 
        typ, data = con.fetch(num, '(RFC822)')
        msgs.append(data)
    return msgs
  
# this is done to make SSL connnection with GMAIL 
con = imaplib.IMAP4_SSL(imap_url)  
  
# logging the user in 
con.login(user, password)  
 
# calling function to check for email under this label 
con.select('Inbox')  
  
# Empty list for adding suspicious users/groups to
suspicious_users = []
suspicious_groups = []
suspicious_principals = []

# Looping through email alerts for dectecting
msgs_log_analytics = get_emails(search('SUBJECT', 'Alert Notification', con))
for email_log_analytics in msgs_log_analytics[::-1]:
	for emai_log in email_log_analytics:
		if type(emai_log) is tuple:
			email_content = str(emai_log[1], 'utf-8')
			data = str(email_content)
			mail_content2 = mailparser.parse_from_string(email_content)
			email_body = mail_content2.body
			email_soup = bs(email_body,"html.parser")
			parsed_email_log_values = []
			for parsed_email_values_log_content in email_soup.select('th[style*="360px"]'):
				parsed_email_log_values.append(parsed_email_values_log_content.get_text())
			timestamp = parsed_email_log_values[2]
			userPrincipalName = json.loads(parsed_email_log_values[15])['user']['userPrincipalName']
			role_name = json.loads(parsed_email_log_values[18])
			print("\n--------- Azure Alert ---------")
			print("Alert type: GlobalAdminDetect" )
			print("Event: Add member to role")
			print("Action performed by: "+ userPrincipalName)
			print("Time: "+ timestamp)
			print("Action: The User "+ role_name[0]['userPrincipalName'] +" was added to the subscription as "+ str(role_name[0]['modifiedProperties'][1]['newValue']))
			suspicious_users.append(role_name[0]['userPrincipalName'].rstrip())
	print("--------- END ---------")

msgs = get_emails(search('SUBJECT', 'Azure Monitor', con))

for msg in msgs[::-1]:
    for email in msg:    
        if type(email) is tuple:  
            soup = extract_html(email)
            print("\n--------- Azure Alert ---------")
            # Parsing the contents of the emails
            # Identify the values. For example: Actvity log alert: AzureAutomationRunbookRun. AzureAutomationRunbookRun is what we are after here.
            parsed_email = parse_html(soup)
            # Main data structure
            alert_type = parsed_email['activity log alert']
            event = parsed_email['operation name']
            action_caller = parsed_email['caller']
            timestamp = parsed_email['time']


            # The alert names are hardcoded
            supported_alerts = ["Webhook", "SubscriptionMonitor", "AutomationAccountDetect", "GlobalAdminDetect"]
            if alert_type in supported_alerts:
            	if "Webhook" in alert_type:
            		print("Webhook Logic")
            	elif "AutomationAccount" in alert_type:
            		action_caller = parsed_email['caller']
            		timestamp = parsed_email['time']
            		resource_id = parsed_email['resource id'].split("/")
            		print("Alert type: " +alert_type)
            		print("Event: New Automation Account was created")
            		print("Action performed by: "+ action_caller)
            		print("Time: "+ timestamp)
            		print("Action: The " +str(resource_id[8].rstrip()) + "automation account was created by "+ action_caller)
            		suspicious_principals.append(resource_id[8].rstrip())
            	elif "SubscriptionMonitor" in alert_type:
            		# Main structure
            		print("Alert type: " +alert_type)
            		print("Event: "+event)
            		print("Action performed by: "+ action_caller)
            		print("Time: "+ timestamp)
            		# Data body
            		properties = parsed_email['properties']
            		json_body = json.loads(properties)
            		json_body_request_body = json_body['requestbody']
            		json_body_request_body_parsed = json.loads(json_body_request_body)
            		json_body = json.loads(properties)
            		try:
            			PrincipalType = (json_body_request_body_parsed['Properties']['PrincipalType'])
            			service_principal_id = json_body_request_body_parsed['Properties']['PrincipalId']
            			role_name = get_azure_role_from_id(json_body_request_body_parsed['Properties']['RoleDefinitionId'].split("/")[4])
            			if "User" in PrincipalType:
            				userPrincipalName = getUserPrincipalName(service_principal_id)
            				print("Action: The user "+ userPrincipalName +" was added to the subscription as "+ str(role_name))
            				if "Owner" in role_name:
            					suspicious_users.append(userPrincipalName.rstrip())
            			elif "Group" in PrincipalType:
            				print("Action: The Group "+ getADGroupName(service_principal_id) +" was added to the subscription as "+ str(role_name))
            				if "Owner" in role_name:
            					suspicious_groups.append(getADGroupName(service_principal_id).rstrip())
            			elif "ServicePrincipal" in PrincipalType:
            				print("Action: The Service Principal "+ getServicePrincipalName(service_principal_id).rstrip() +" was added to the subscription as "+ str(role_name))
            				if isAutomationAccount(service_principal_id):
            					print("Attention: the "+ getServicePrincipalName(service_principal_id).rstrip()+ "user is an Automation account")
            				if "Owner" in role_name:
            					suspicious_principals.append(getServicePrincipalName(service_principal_id).rstrip())
            		except:
            			# This is hardcoded for now. For some reason, the output is different when adding/creating a new AD user as Owner from a Runbook
            			role_name = get_azure_role_from_id(json_body_request_body_parsed['properties']['roleDefinitionId'].split("/")[6])
            			PrincipalType = "User"
            			service_principal_id = json_body_request_body_parsed['properties']['principalId']
            			userPrincipalName = subprocess.check_output("az ad user show --id "+service_principal_id+" |jq -r '.userPrincipalName'", shell=True)
            			print("Action: The user "+ userPrincipalName.decode("utf-8").rstrip() +" was added to the subscription as "+str(role_name) )
            			if "Owner" in role_name:
            				suspicious_users.append(userPrincipalName.decode("utf-8").rstrip())		
            else:
                print("Not currently supported")
                break
            print("--------- END ---------")

# Results Summary
suspicious_users = list(dict.fromkeys(suspicious_users))
suspicious_groups = list(dict.fromkeys(suspicious_groups))
suspicious_principals = list(dict.fromkeys(suspicious_principals))
print("\n--------- Summary ---------")
print("Suspicious Users detected: "+ str(suspicious_users))
print("Suspicious Groups detected: "+ str(suspicious_groups))
print("Suspicious Service Principals detected: "+ str(suspicious_principals))
print("--------- End of Summary ---------")
