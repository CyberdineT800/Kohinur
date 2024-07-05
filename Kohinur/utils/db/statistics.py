from utils.db.postgres import Database

class Statistics(Database):
    async def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Statistics (
            statistics_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            teacher_id BIGINT,
            student_id BIGINT,
            subject_id BIGINT,
            correct_answers_count INT,
            all_tests_count INT,
            statistics_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirm BOOLEAN DEFAULT FALSE
        );
        """
        await self.execute(sql, execute=True)

    async def add_statistics(self, data):
        columns = ["teacher_id", "student_id", "subject_id", 
                   "correct_answers_count", "all_tests_count", "confirm"]
        placeholders = ", ".join(f"${i}" for i in range(1, len(columns) + 1))
        sql = f"INSERT INTO Statistics ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
    
        values = [
            data['teacher_id'],
            data['student_id'],
            data['subject_id'],
            data['correct_answers_count'],
            data['all_tests_count'],
            data.get('confirm', False) 
        ]
    
        return await self.execute(sql, *values, fetchrow=True)

    async def update_statistics(self, data):
        sql = """
        UPDATE Statistics
        SET  
            teacher_id = $2,
            student_id = $3,
            subject_id = $4,
            correct_answers_count = $5,
            all_tests_count = $6,
            statistics_date = $7,
            confirm = $8
        WHERE statistics_id = $1
        RETURNING *
        """
        return await self.execute(sql,
                                  data['statistics_id'],
                                  data['teacher_id'],
                                  data['student_id'],
                                  data['subject_id'],
                                  data['correct_answers_count'],
                                  data['all_tests_count'],
                                  data['statistics_date'],
                                  data.get('confirm', False), 
                                  fetchrow=True)

    async def select_all_statistics(self):
        sql = "SELECT * FROM Statistics"
        return await self.execute(sql, fetch=True)

    async def select_statistics(self, **kwargs):
        kwargs = {key: value for key, value in kwargs.items()}
        sql = "SELECT * FROM Statistics WHERE 1=1 AND "
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

    async def count_statistics(self):
        sql = "SELECT COUNT(*) FROM Statistics"
        return await self.execute(sql, fetchval=True)
    
    async def delete_statistics_by_id(self, statistics_id):
        sql = "DELETE FROM Statistics WHERE statistics_id = $1"
        await self.execute(sql, statistics_id, execute=True)

    async def upsert_statistics(self, data):
        if 'statistics_id' in data:
            updated_statistics = await self.update_statistics(data)
            if updated_statistics:
                return updated_statistics
        
        new_statistics = await self.add_statistics(data)
        return new_statistics
