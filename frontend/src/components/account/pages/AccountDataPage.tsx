import { useEffect, useState } from 'react';

import { getPrivacyInfo, requestAccountDeletion, requestDataExport } from '../../../services/account.service';
import type { AccountPrivacy } from '../../../types/account';
import { DataControlsPanel } from '../DataControlsPanel';

export function AccountDataPage() {
  const [privacy, setPrivacy] = useState<AccountPrivacy | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    void getPrivacyInfo().then(setPrivacy);
  }, []);

  return (
    <div className="space-y-3">
      <DataControlsPanel
        privacy={privacy}
        onExport={async () => {
          const response = await requestDataExport();
          setFeedback(response.message);
        }}
        onDeleteRequest={async () => {
          const confirmed = window.confirm('Deseja realmente solicitar exclusao da conta?');
          if (!confirmed) return;
          const response = await requestAccountDeletion();
          setFeedback(response.message);
        }}
      />
      {feedback ? <p className="text-sm text-cyan">{feedback}</p> : null}
    </div>
  );
}
