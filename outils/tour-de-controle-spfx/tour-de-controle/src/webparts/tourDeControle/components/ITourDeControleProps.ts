import type { SPHttpClient } from '@microsoft/sp-http';

export interface ITourDeControleProps {
  description: string;
  isDarkTheme: boolean;
  environmentMessage: string;
  hasTeamsContext: boolean;
  userDisplayName: string;
  /** Client REST du contexte SPFx — lecture des listes du site (SSO, zéro secret). */
  spHttpClient: SPHttpClient;
  /**
   * URL absolue du site où vivent les listes (modele-donnees §2 bis) — base des
   * appels `_api/web/lists`. Peut différer du site de la page (défaut = site courant).
   */
  dataSiteUrl: string;
}
