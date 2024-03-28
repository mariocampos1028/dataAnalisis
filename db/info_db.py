from db.cliente import db_cliente
from models.find_user_model import find_user_model
from bson.objectid import ObjectId
from typing import Any

def save_collections_many(list_dic:list, user:str):
    try:
        idcount= find_user_and_count(user)
        for item in list_dic:
            item["data_owner_user"] = user
            item["id_user_count"] = idcount
            result = db_cliente.local.data.insert_one(dict(item))
            item["_id"] = str(result.inserted_id)
        #db_cliente.close()
    except:
        return 0
    return 1

def find_one_by(field:str, value_str: str = None, value_int: int = None ):
    return 2 


def find_user_and_count(user:str):
    cant = db_cliente.local.data.count_documents({"data_owner_user":user}) 
    if cant > 0:   
        max_id_user_count = db_cliente.local.data.find({"data_owner_user": user}).sort([("id_user_count", -1)]).limit(1)
        for doc in max_id_user_count:
            max_id_user_count_value = doc["id_user_count"]
        return max_id_user_count_value+1
    else:
        return 1
        

def find_collections(user:str):
    cant  = db_cliente.local.data.count_documents({"data_owner_user":user})
    collecttions_info_list = []
    collecttions_info_dict = {}
    if cant > 0:
        pipeline = [
        {'$match': {'data_owner_user': user} },
        {'$group': {'_id': {'id_user_count': '$id_user_count','data_owner_user': '$data_owner_user'},'count': {'$sum': 1}}},
        {'$sort': {'_id.id_user_count': 1}}
        ]
        resultado_prueba = db_cliente.local.data.aggregate(pipeline=pipeline)
        list_resultado_prueba = list(resultado_prueba)
        for item in list_resultado_prueba:
           collecttions_info_dict["user"] = item["_id"]["data_owner_user"]
           collecttions_info_dict["id_user_count"] = item["_id"]["id_user_count"]
           collecttions_info_dict["numberRecords"] = item["count"]
           collecttions_info_list.append(collecttions_info_dict)
           collecttions_info_dict = {}
        return collecttions_info_list
    else:
        return {"message":"no existen registros para el usuario"}

def delete_collection(user:str, id_user_count:int):
    result = db_cliente.local.data.delete_many({"data_owner_user":user , "id_user_count":id_user_count})
    return result.deleted_count

def delete_all_collections(user:str):
    result = db_cliente.local.data.delete_many({"data_owner_user":user})
    return result.deleted_count


def find_register(id:str):
    result = db_cliente.local.data.find_one({"_id":ObjectId(str(id))})
    if result is None:
        return {"message":"no existe registro con el id especificado"}
    else:
         result["_id"] = str(result.pop("_id"))
    return result

def find_a_collection(user:str, id_user_count:int):
    count = db_cliente.local.data.count_documents({"data_owner_user":user , "id_user_count":id_user_count})
    result = db_cliente.local.data.find({"data_owner_user":user , "id_user_count":id_user_count})
    data_list = []
    if count>0:
        for document in result:            
            new_document = {}
            for key, value in document.items():
                new_document[key] = value    
            new_document.pop("_id")
            new_document["_id"] = str(document["_id"])
            data_list.append(new_document)            
        return data_list
    else:
        return {"message":"no se encontro ningina collection con los parametros ingresados"}
        
def update_register(user:str, id:str, name_field:str, value_field:Any):
    
    if validate_exist_field_document(id,name_field) == False:
        return {"message":f"campo {name_field} no existente"}  
    result = db_cliente.local.data.update_one({"_id":ObjectId(str(id))},{"$set":{f"{name_field}":value_field}})
    res = find_register(id)
    return res
    
    
def update_field_collection(user:str, id_user_count:int, name_field:str, value_field:Any):
    result = db_cliente.local.data.update_many({"data_owner_user":user , "id_user_count":id_user_count},{"$set":{f"{name_field}":value_field}})
    if validate_exist_collection(user, id_user_count):
        return {"message":f"se actualizaron {result.modified_count} registros correctamente"}
    else:
        return {"message":f"No existe la colleccion especificada definida para la combinacion: {user} / {id_user_count} por favor validar!"}

def validate_exist_collection(user:str,id_user_count:int):
    count = db_cliente.local.data.count_documents({"data_owner_user":user , "id_user_count":id_user_count})
    if count > 0:
        return True
    else:
        return False

def validate_exist_field_document(id:str, name_field:str):
    res = find_register(id)
    exist_name = False
    for key,value in res.items():
        if key == name_field:
            exist_name = True
    return exist_name


def delete_field_collection(user:str, id_user_count:int, name_field:str):
    if validate_exist_collection(user,id_user_count):    
        result = db_cliente.local.data.update_many({"data_owner_user":user , "id_user_count":id_user_count},{"$unset":{f"{name_field}":""}})
        return {"message":f"registros modificados {result.modified_count}"}
    else:
        return {"message":f"No existe la colleccion especificada definida para la combinacion: {user} / {id_user_count} por favor validar!"}

def downloadfile_csv(user:str, id_user_count):
    count = db_cliente.local.data.count_documents({"data_owner_user":user , "id_user_count":id_user_count})
    result = db_cliente.local.data.find({"data_owner_user":user , "id_user_count":id_user_count})
    data_list = []
    if count>0:
        for document in result:            
            new_document = {}
            for key, value in document.items():
                new_document[key] = value    
            new_document.pop("_id")
            new_document.pop("data_owner_user")
            new_document.pop("id_user_count")
            data_list.append(new_document)            
        return data_list
    else:
        return {"message":"no se encontro ningina collection con los parametros ingresados"}