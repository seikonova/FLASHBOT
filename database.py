import aiosqlite
from datetime import datetime

DB_FILE = "db.db"


class DBFunctions:

    @staticmethod
    async def get_admin_messages(limit=50):
        async with aiosqlite.connect(DB_FILE) as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute("""
                SELECT
                    am.id,
                    am.order_id,
                    am.user_id,
                    am.telegram_message_id,
                    am.message_text,
                    am.created_at,
                    o.order_number,
                    o.name,
                    o.username
                FROM admin_messages am
                LEFT JOIN orders o ON o.id = am.order_id
                ORDER BY am.created_at DESC
                LIMIT ?
            """, (limit,))

            rows = await cursor.fetchall()
            return rows

    @staticmethod
    async def get_new_orders():
        async with aiosqlite.connect(DB_FILE) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("""
                SELECT id, order_number, user_id, username, name, product_type,
                       size, model, comment, status, created_at
                FROM orders
                WHERE status = 'new'
                ORDER BY id DESC
            """)
            return await cursor.fetchall()

    @staticmethod
    async def get_all_orders():
        async with aiosqlite.connect(DB_FILE) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("""
                SELECT id, order_number, user_id, username, name, product_type,
                       size, model, comment, status, created_at
                FROM orders
                ORDER BY id DESC
            """)
            return await cursor.fetchall()

    @staticmethod
    async def get_order(order_id: int):
        async with aiosqlite.connect(DB_FILE) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("""
                SELECT id, order_number, user_id, username, name, product_type,
                       size, model, comment, status, created_at, answered_at
                FROM orders
                WHERE id = ?
            """, (order_id,))
            return await cursor.fetchone()

    @staticmethod
    async def update_order_status(order_id: int, status: str):
        async with aiosqlite.connect(DB_FILE) as conn:
            await conn.execute(
                "UPDATE orders SET status = ? WHERE id = ?",
                (status, order_id)
            )
            await conn.commit()

    @staticmethod
    async def save_admin_response(order_id: int, response: str):
        async with aiosqlite.connect(DB_FILE) as conn:
            await conn.execute(
                """UPDATE orders
                   SET admin_response = ?, answered_at = ?
                   WHERE id = ?""",
                (response, datetime.now().isoformat(), order_id)
            )
            await conn.commit()

    @staticmethod
    async def get_user_orders(user_id: int):
        async with aiosqlite.connect(DB_FILE) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("""
                SELECT id, order_number, name, product_type, size, model,
                       comment, status, created_at
                FROM orders
                WHERE user_id = ?
                ORDER BY id DESC
            """, (user_id,))
            return await cursor.fetchall()

    @staticmethod
    async def generate_order_number(
        user_id: int,
        name: str,
        product_type: str,
        size: str | None,
        model: str | None,
        comment: str | None,
        username: str | None = None
    ) -> str:
        created_at = datetime.now().isoformat()

        async with aiosqlite.connect(DB_FILE) as conn:
            cursor = await conn.execute(
                """
                INSERT INTO orders (
                    user_id, username, name, product_type, size, model,
                    comment, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id, username, name, product_type, size, model,
                    comment, "new", created_at
                )
            )

            order_id = cursor.lastrowid
            order_number = f"FLASH-{order_id:06d}"

            await conn.execute(
                "UPDATE orders SET order_number = ? WHERE id = ?",
                (order_number, order_id)
            )
            await conn.commit()

            return order_number

    @staticmethod
    async def save_admin_message(
        order_id: int,
        user_id: int,
        telegram_message_id: int,
        message_text: str | None = None
    ):
        """Сохраняет сообщение админа, чтобы пользователь мог ответить Reply."""
        async with aiosqlite.connect(DB_FILE) as conn:
            await conn.execute(
                """
                INSERT INTO admin_messages (
                    order_id, user_id, telegram_message_id, message_text, created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order_id, user_id, telegram_message_id,
                    message_text, datetime.now().isoformat()
                )
            )
            await conn.commit()

    @staticmethod
    async def get_order_by_admin_message_id(telegram_message_id: int):
        """Находит заказ по ID сообщения администратора."""
        async with aiosqlite.connect(DB_FILE) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                SELECT o.id, o.order_number, o.user_id, o.username, o.name,
                       o.product_type, o.size, o.model, o.comment, o.status,
                       o.created_at, o.answered_at
                FROM admin_messages am
                JOIN orders o ON o.id = am.order_id
                WHERE am.telegram_message_id = ?
                LIMIT 1
                """,
                (telegram_message_id,)
            )
            return await cursor.fetchone()


async def init_db(db_file: str = DB_FILE):
    try:
        conn = await aiosqlite.connect(db_file)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE,
                user_id INTEGER NOT NULL,
                username TEXT,
                name TEXT NOT NULL,
                product_type TEXT NOT NULL,
                size TEXT,
                model TEXT,
                comment TEXT,
                status TEXT NOT NULL DEFAULT 'new',
                admin_response TEXT,
                created_at TEXT NOT NULL,
                answered_at TEXT
            )
        """)

        cursor = await conn.execute("PRAGMA table_info(orders)")
        columns = await cursor.fetchall()
        column_names = [column[1] for column in columns]

        if "model" not in column_names:
            await conn.execute("ALTER TABLE orders ADD COLUMN model TEXT")
            print("✅ В таблицу orders добавлена колонка model")

        if "username" not in column_names:
            await conn.execute("ALTER TABLE orders ADD COLUMN username TEXT")
            print("✅ В таблицу orders добавлена колонка username")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS admin_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                telegram_message_id INTEGER NOT NULL UNIQUE,
                message_text TEXT,
                created_at TEXT NOT NULL
            )
        """)

        await conn.commit()
        print("✅ База данных инициализирована")
        return conn

    except aiosqlite.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return None


async def client_form(
    user_id: int,
    name: str,
    product_type: str,
    size: str | None,
    model: str | None,
    comment: str | None
):
    return await DBFunctions.generate_order_number(
        user_id=user_id,
        name=name,
        product_type=product_type,
        size=size,
        model=model,
        comment=comment
    )
