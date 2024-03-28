from fastapi import APIRouter, UploadFile
from fastapi.exceptions import HTTPException
import pandas as pd
import io
from io import BytesIO
import db.info_db as save
from db.cliente import db_cliente
from models.find_user_model import find_user_model
import re
from typing import Any, List
from fastapi.responses import Response
import csv

router = APIRouter(prefix="/data")


@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile, user : str):
    
    if file.content_type != 'text/csv':
        raise HTTPException(400,"Invalid document type")
    else:
        content = await file.read()    
        file_obj = io.BytesIO(content)
        
        # Abrimos el archivo CSV en modo lectura
        df = pd.read_csv(file_obj,sep='[;,:]',engine='python')
        dict_data = df.to_dict(orient="records")        
        save.save_collections_many(dict_data,user)           
        
    return dict_data

@router.get("/find_collections")
async def find_collections(user:str):
    return save.find_collections(user)



@router.delete("/delete_collection")
async def delete_collection(user:str, id_user_count:int):
    res = save.delete_collection(user, id_user_count)
    if(res>0):
        return {"message":f"se eliminaron {res} registros"}
    else:
        return {"message":f"no se encontraron registros para:  user: {user} / id_user_count: {id_user_count}"}


@router.delete("/delete_all_collections")
async def delete_all_collections(user:str):
    res = save.delete_all_collections(user)
    if(res>0):
        return {"message":f"se eliminaron {res} registros"}
    else:
        return {"message":f"no se encontraron registros para:  user: {user}"}


@router.get("/find_register")
async def find_register(id:str):
    patron_object_id = re.compile(r'^[0-9a-fA-F]{24}$')
    if bool(patron_object_id.match(id)):
        return save.find_register(id)
    else:
        return {"message":"La cadena no es un ObjectId válido"}    
    
    

@router.get("/find_a_collection")
async def find_a_collection(user:str, id_user_count: int):
    res = save.find_a_collection(user,id_user_count)
    return res

@router.put("/update_register")
async def update_register(user:str,id:str, name_field:str, value: Any):
    patron_object_id = re.compile(r'^[0-9a-fA-F]{24}$')
    if bool(patron_object_id.match(id)):
        return save.update_register(user, id, name_field, value)
    else:
        return {"message":"La cadena no es un ObjectId válido"}


@router.put("/update_field_collection")
async def update_field_collection(user:str, id_user_count:int, name_field:str, value_field:Any):
    return save.update_field_collection(user, id_user_count, name_field, value_field)


@router.delete("/delete_field_collection")
async def delete_field_collection(user:str, id_user_count:int, name_field:str):
    return save.delete_field_collection(user,id_user_count,name_field)


@router.post("/save_collection")
async def save_collection(json_data: List[dict],user:str):
    if isinstance(json_data, list):        
        received_list = json_data
        for item in received_list:
            if "_id" in item:
                del item["_id"]
            if "data_owner_user" in item:
                del item["data_owner_user"]
            if "id_user_count" in item:
                del item["id_user_count"]            
             
        res = save.save_collections_many(received_list,user)
        if res == 1:
            return {"message":"Guardado correctamente!!"}
        else:
            return {"message":"Error al guardar"}
    else:
        # Si no es una lista, intenta convertir el JSON en una lista
        received_list = []
        for key, value in json_data.items():
            received_list.append(value)
        return {"message":"Error: json no valido"}
    
@router.post("/uploadfile_xlsx")
async def uploadfile_xlsx(file: UploadFile, user : str):
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise HTTPException(400,"Invalid document type")
    else:
        content = await file.read()    
        file_obj = io.BytesIO(content)
        
        # Abrimos el archivo CSV en modo lectura
        df = pd.read_excel(file_obj)
        dict_data = df.to_dict(orient="records")        
        save.save_collections_many(dict_data,user)
    return dict_data

@router.get("/downloadfile_csv")
async def uploadfile_xlsx(user:str, id_user_count: int):
    data = save.downloadfile_csv(user,id_user_count)
    filename="data.csv"
    if type(data) == list:
        
        df = pd.DataFrame(data)
        csv_content = df.to_csv(index=False)
    else:
        return data
    
    return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition":f"attachment;filename={filename}"})
    

@router.get("/downloadfile_xlsx")
async def uploadfile_xlsx(user:str, id_user_count: int):
    data = save.downloadfile_csv(user,id_user_count)
    filename="data.xlsx"
    if type(data) == list:
        excel_file = BytesIO()
        df = pd.DataFrame(data)
        df.to_excel(excel_file,index=False)        
        
    else:
        return data
    
    return Response(content=excel_file.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition":f"attachment;filename={filename}"})
    
