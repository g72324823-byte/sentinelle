select tx_id, ts, cast(ts as date) as jour, compte_id, type as type_tx, montant,
       compte_dest, agent_id, pays, ville, canal, device_id, est_fraude
from {{ source('brut', 'transactions') }}
where montant > 0
