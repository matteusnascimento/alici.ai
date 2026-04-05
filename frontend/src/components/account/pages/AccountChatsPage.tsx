import { useEffect, useState } from 'react';

import { getArchivedChats } from '../../../services/account.service';
import type { AccountArchivedChatList } from '../../../types/account';
import { ArchivedChatsPanel } from '../ArchivedChatsPanel';

export function AccountChatsPage() {
  const [data, setData] = useState<AccountArchivedChatList | null>(null);

  useEffect(() => {
    void getArchivedChats().then(setData);
  }, []);

  return <ArchivedChatsPanel data={data} />;
}
