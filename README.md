# Função Lambda para Upload de Arquivos para S3

Esta função Lambda em Python permite fazer o upload de arquivos para um bucket S3 e gerar uma URL pré-assinada para acessar o arquivo. A URL pré-assinada tem um tempo de expiração definido para garantir a segurança.

## Configurações Necessárias

### Configurações no S3

1. **Criação do Bucket:**
   - Crie um bucket S3 ou utilize um existente.
   - Atualize o nome do bucket no código (`BUCKET_NAME`).

2. **Políticas do Bucket:**
   - Adicione as seguintes políticas ao bucket S3 para permitir acesso pela função Lambda:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Principal": {
                   "Service": "lambda.amazonaws.com"
               },
               "Action": [
                   "s3:PutObject",
                   "s3:GetObject",
                   "s3:DeleteObject"
               ],
               "Resource": "arn:aws:s3:::your-bucket-name/*",
               "Condition": {
                   "ArnLike": {
                       "aws:SourceArn": "arn:aws:lambda:us-east-1:your-account-id:function:your-lambda-function-name"
                   }
               }
           }
       ]
   }
   ```

### Configurações no API Gateway

1. **Criação da API:**
   - Crie uma nova API no API Gateway.
   - Configure um novo método POST para a API.
   - Integre o método com a função Lambda.

2. **Habilitar Suporte a Binários:**
   - No método POST, adicione um mapeamento de conteúdo binário para garantir que arquivos binários sejam corretamente processados.

### Configurações no IAM

1. **Permissões para a Função Lambda:**
   - Crie uma função IAM com as permissões necessárias para acessar o bucket S3:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:PutObject",
                   "s3:GetObject",
                   "s3:DeleteObject"
               ],
               "Resource": "arn:aws:s3:::your-bucket-name/*"
           }
       ]
   }
   ```
   - Anexe essa política à função Lambda.

## Exemplo de Requisição no Postman

Para testar a função Lambda via API Gateway utilizando o Postman, siga os passos abaixo:

1. **URL da Requisição:**
   ```
   https://your-api-id.execute-api.us-east-1.amazonaws.com/your-stage/upload?file_name=example.jpg
   ```

2. **Método:**
   ```
   POST
   ```

3. **Headers:**
   - `x-api-key`: Chave da API do API Gateway.
   - `Content-Type`: Tipo de conteúdo do arquivo (exemplo: `image/jpeg`).

4. **Body:**
   - Selecione a opção `binary`.
   - Faça o upload do arquivo que deseja enviar.

## Código da Função Lambda

```python
import json
import boto3
import base64

s3_client = boto3.client('s3')
BUCKET_NAME = 'your-bucket-name'

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(event['body'])
        else:
            body = event['body'].encode('utf-8')
        print("Body length:", len(body))
        
        content_type = event['headers'].get('Content-Type', 'application/octet-stream')
        print("Content type:", content_type)
        
        key = event['queryStringParameters']['file_name']
        print("File name:", key)
        
        response = s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=body,
            ContentType=content_type
        )
        print("S3 Response:", response)
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=604800  # URL válida por 7 dias (máximo permitido)
        )
        print("Presigned URL:", presigned_url)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, x-api-key',
                'Access-Control-Allow-Methods': 'POST'
            },
            'body': json.dumps({'message': 'File uploaded successfully', 'file_url': presigned_url})
        }
    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, x-api-key',
                'Access-Control-Allow-Methods': 'POST'
            },
            'body': json.dumps({'message': 'File upload failed', 'error': str(e)})
        }
```

Este exemplo de código mostra como configurar uma função Lambda para fazer upload de arquivos para um bucket S3 e gerar uma URL pré-assinada para acessar o arquivo. Ajuste os parâmetros e configurações conforme necessário para seu uso específico.
