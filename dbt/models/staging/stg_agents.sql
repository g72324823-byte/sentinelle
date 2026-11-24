-- Dernière version connue de chaque agent (le fichier du jour le plus récent gagne)
with src as (
    select *, regexp_extract(filename, 'agents_(\d{8})', 1) as jour_fichier
    from {{ source('brut', 'agents') }}
)
select agent_id, type as type_agent, categorie, pays, ville,
       cast(date_agrement as date) as date_agrement, statut,
       strptime(jour_fichier, '%Y%m%d')::date as date_fichier
from src
qualify row_number() over (partition by agent_id order by jour_fichier desc) = 1
