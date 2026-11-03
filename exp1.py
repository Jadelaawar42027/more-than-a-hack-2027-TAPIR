from kloppy import metrica

ds = metrica.load_tracking_epts(
    meta_data="data/tactical/BAR-ATH_tactical_atd.xml",
    raw_data="data/tactical/BAR-ATH_tactical_atd.txt",
)

# 1. Does the metadata know the teams?
for team in ds.metadata.teams:
    print(team.name, "-", len(team.players), "track slots")

# 2. Are ownership and ball state filled in?
for row in [11185, 12000, 15000]:
    f = ds.records[row]
    print(row, "owner:", f.ball_owning_team, "| state:", f.ball_state)

owned = sum(1 for f in ds.records if f.ball_owning_team is not None)
stated = sum(1 for f in ds.records if f.ball_state is not None)
print("frames with owner:", owned, "| frames with state:", stated, "| total:", len(ds.records))