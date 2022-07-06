from sqlalchemy.orm import Session
from src.services import cognito
from src.core import tables, deps

def migrate_workspaces():
    db = next(deps.get_db())
    #print(db)
    res, err = cognito.list_groups()
    if res :
        #group_names = tuple([ x['GroupName'] for x in res['Groups']])
        #matched = db.query(tables.Workspace).filter(tables.Workspace.name.in_(group_names)).all()
        #print(matched)
        for g in res['Groups']:
            ## refactor to https://stackoverflow.com/a/41951905/1226748
            if not db.query(tables.Workspace).filter(tables.Workspace.name == g['GroupName']).first():
                print('migrating => ', g['GroupName'])
                db_obj = tables.Workspace(
                    name=g['GroupName'],
                    creator_id='9004ff5e-20bd-49dc-ba00-2f4dafac9940', ## jimmy-cognito-id
                    description=g['Description'],
                    created_at=g['CreationDate'],
                    updated_at=g['LastModifiedDate'],
                )
                db.add(db_obj)
                db.commit()

