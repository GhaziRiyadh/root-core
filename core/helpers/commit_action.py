from typing import List, TypeVar, Generic, Literal
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


class CommitAction(Generic[T]):
    async def commit(
        self,
        db: AsyncSession,
        obj: T | List[T],
        action: Literal["CREATE", "UPDATE", "DELETE", "RESTORE"],
    ) -> None:
        """This function to handle commit any thing to db and add other actions like before and after.
            Every action has params (db: AsyncSession,obj:T)

        Actions:
            before_action: call before commit action call
            after_action: call after commit and refresh action call

        Args:
            db (AsyncSession): _description_
            obj (T): _description_
            action (Literal[&quot;CREATE&quot;, &quot;UPDATE&quot;, &quot;DELETE&quot;]): _description_

        """
        before_action = f"before_{action.lower()}"
        after_action = f"after_{action.lower()}"

        if hasattr(self, before_action):
            await getattr(self, before_action)(db, obj)

        await db.commit()
        if isinstance(obj, List):
            for o in obj:
                await db.refresh(o)
        else:
            await db.refresh(obj)

        if hasattr(self, after_action):
            await getattr(self, after_action)(db, obj)
