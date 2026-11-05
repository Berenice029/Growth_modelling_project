import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

# 1. Ta fonction vitale
def detect_test(ch):
    if pd.isna(ch): return "Missing"
    elif re.search(r"test", str(ch), re.IGNORECASE): return "Test"
    else: return "Real"

# [...] (Je passe le chargement basique des 4 CSV)

# 2. LES CORRECTIONS MAJEURES À AJOUTER À TON NETTOYAGE :

# A. Les dates dans booking_requests et marketing_spend sont souvent au format européen (27/02/2026).
# Il faut impérativement forcer l'argument dayfirst=True sinon Python se trompe de mois !
booking_requests_df['request_date'] = pd.to_datetime(booking_requests_df['request_date'], dayfirst=True, errors='coerce')
marketing_spend_df['month'] = pd.to_datetime(marketing_spend_df['month'], dayfirst=True, errors='coerce')

# B. Standardisation des villes : "Lyon 3e", "PARIS 11", "lyon"... vont fausser tes agrégations.
booking_requests_df['city'] = booking_requests_df['city'].astype(str).str.title().str.strip()
booking_requests_df['city'] = booking_requests_df['city'].apply(lambda x: 'Lyon' if 'Lyon' in x else ('Paris' if 'Paris' in x else x))


# 3. LE SCRIPT POUR LA QUESTION 4 (À exécuter après le nettoyage) :

# On crée des périodes mensuelles
booking_requests_df['month_period'] = booking_requests_df['request_date'].dt.to_period('M')
marketing_spend_df['month_period'] = marketing_spend_df['month'].dt.to_period('M')

# A - Évolution du taux de "Unfulfilled" (requêtes annulées faute de cleaner)
status_counts = booking_requests_df.groupby(['month_period', 'city', 'status']).size().unstack(fill_value=0)
status_counts['total_requests'] = status_counts.sum(axis=1)
status_counts['unfulfilled_rate_pct'] = (status_counts['unfulfilled'] / status_counts['total_requests']) * 100

print("--- Taux d'échec (Unfulfilled %) par ville ---")
display(status_counts[['unfulfilled_rate_pct']].unstack('city').round(1))

# B - Évolution du budget (Demande/Clients vs Offre/Cleaners)
spend_trends = marketing_spend_df.groupby(['month_period', 'side'])['spend_eur'].sum().unstack(fill_value=0)
print("\n--- Dépenses Marketing (Clients vs Cleaners) ---")
display(spend_trends)

# C - Visualisation de la crise à Lyon
lyon_data = status_counts.xs('Lyon', level='city')
plt.figure(figsize=(10, 4))
plt.plot(lyon_data.index.astype(str), lyon_data['unfulfilled_rate_pct'], marker='o', color='red')
plt.title("Explosion du taux de requêtes non satisfaites à Lyon (Manque de Cleaners)")
plt.ylabel("% de requêtes unfulfilled")
plt.xticks(rotation=45)
plt.grid(True)
plt.show()