# -*- coding: utf-8 -*-
from typing import List
from fastapi import APIRouter
from app import schemas
from app.config import get_settings

settings = get_settings()
volumes_root = settings.VOLUMES_ROOT
router = APIRouter()


@router.get("/templates", response_model=List[schemas.App])
async def query_templates():
    return [
        {'name': 'bookkeeping',
         'title': 'bookkeeping', 
         'description': 'lite bookkeeping', 
         'image': 'mblocks/bookkeeping',
         'ingress': [
            {'name':'bookkeeping', 'path': '/bookkeeping', 'target': {'path': '/', 'port': 80}, 'use_auth':{}}
          ],
        },
        {'name': 'drive', 'title': 'Drive', 'description': 'hello drive', 'image': 'mblocks/drive-backend',
            'environment':[
                {'name':'SERVICES_MINIO_HOST','value':'minio.drive.mblocks:9000'},
                {'name':'SERVICES_MINIO_ACCESS_KEY','value':'hello'},
                {'name':'SERVICES_MINIO_SECRET_KEY','value':'helloworld'},
                {'name':'SERVICES_MINIO_PROXY','value':'/api/services/minio'},
            ],
            'ingress': [
                {'name':'drive', 'path': '/drive', 'target': {'path': '/', 'port': 80}, 'use_auth':{}}
            ],
            'roles': [
                { 'title':'admin', 'auth': {} }
            ],
            'depends':[
                {
                    'name':'minio', 
                    'title':'minio', 
                    'image':'minio/minio', 
                    'environment':[
                        {'name':'MINIO_ACCESS_KEY','value':'hello'},
                        {'name':'MINIO_SECRET_KEY','value':'helloworld'},
                        {'name':'MINIO_NOTIFY_WEBHOOK_ENABLE_DRIVE', 'value':'on'},
                        {'name':'MINIO_NOTIFY_WEBHOOK_ENDPOINT_DRIVE', 'value':'http://drive.mblocks/webhooks/minio'}
                    ],
                    'volumes': [{'host_path':'{}/drive/minio/data'.format(volumes_root), 'mount_path':'/data'}] if volumes_root else [],
                    'ingress': [
                        {
                            'name':'minio', 
                            'path': '/api/services/minio', 
                            'target': {'path': '/', 'port': 9000},
                            'middlewares':[
                                {   
                                    'name':'customrequestheaders',
                                    'config':{
                                        'Host':'minio.drive.mblocks:9000'
                                    }
                                },
                            ]
                        }
                    ],
                    'command':["server", "/data"],
                }
            ]
        },
    ]
