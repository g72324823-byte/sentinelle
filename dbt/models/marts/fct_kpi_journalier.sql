-- Indicateurs quotidiens pour le tableau de bord de la direction (À COMPLÉTER)
select jour, pays,
       count(*)                          as nb_transactions,
       sum(montant)                      as volume_xaf,
       sum(est_fraude)                   as nb_fraudes_confirmees,
       sum(case when est_fraude = 1 then montant else 0 end) as montant_fraude_xaf
       -- TODO : taux de fraude en points de base, volume par type de transaction,
       --        nombre d'agents actifs (jointure avec stg_agents)
from {{ ref('stg_transactions') }}
group by all
