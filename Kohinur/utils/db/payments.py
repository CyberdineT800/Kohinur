from utils.db.postgres import Database

class Payments(Database):
    async def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Payments (
            payment_Id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            payment_student_Id BIGINT,
            payment_group_Id BIGINT,
            payment_Amount DECIMAL,
            payment_Date DATE
        );
        """
        await self.execute(sql, execute=True)

    async def add_payment(self, data):
        columns = ["payment_student_Id", "payment_group_Id", "payment_Amount", "payment_Date"]
        placeholders = ", ".join(f"${i}" for i in range(1, len(columns) + 1))
        sql = f"INSERT INTO Payments ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
    
        values = [
            data['payment_student_id'],
            data['payment_group_id'],
            data['payment_amount'],
            data['payment_date']
        ]
    
        return await self.execute(sql, *values, fetchrow=True)

    async def update_payment(self, data):
        sql = """
            UPDATE Payments
            SET  
                payment_student_Id = $2,
                payment_group_Id = $3,
                payment_Amount = $4, 
                payment_Date = $5
            WHERE payment_Id = $1
            RETURNING *
            """
        return await self.execute(sql,
                                  data['payment_id'],
                                  data['payment_student_id'],
                                  data['payment_group_id'],
                                  data['payment_amount'],
                                  data['payment_date'],
                                  fetchrow=True)

    async def select_all_payments(self):
        sql = "SELECT * FROM Payments"
        return await self.execute(sql, fetch=True)

    async def select_payment(self, **kwargs):
        kwargs = {key: value for key, value in kwargs.items()}
        sql = "SELECT * FROM Payments WHERE 1=1 AND "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    def format_args(self, sql, parameters):
        sql_parts = []
        args = []
        for idx, (key, value) in enumerate(parameters.items(), 1):
            sql_parts.append(f"{key} = ${idx}")
            args.append(value)
        sql += " AND ".join(sql_parts)
        return sql, args

    async def count_payments(self):
        sql = "SELECT COUNT(*) FROM Payments"
        return await self.execute(sql, fetchval=True)
    
    async def delete_payment_by_id(self, payment_id):
        sql = "DELETE FROM Payments WHERE payment_Id = $1"
        await self.execute(sql, payment_id, execute=True)

    async def upsert_payment(self, data):
        if 'payment_id' in data:
            updated_payment = await self.update_payment(data)
            if updated_payment:
                return updated_payment
        
        new_payment = await self.add_payment(data)
        return new_payment
