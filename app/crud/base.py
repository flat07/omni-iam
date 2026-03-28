class BaseCRUD:
    def __init__(self, model):
        self.model = model

    def get_all(self, db, context):
        return db.query(self.model).filter(
            self.model.vendor_id == context["vendor_id"]
        ).all()

    def get(self, db, id, context):
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.vendor_id == context["vendor_id"]
        ).first()

    def create(self, db, obj_in, context):
        obj = self.model(**obj_in.dict(), vendor_id=context["vendor_id"])
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db, id, context):
        obj = self.get(db, id, context)
        if not obj:
            return None
        db.delete(obj)
        db.commit()
        return obj