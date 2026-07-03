import type { SPHttpClient } from '@microsoft/sp-http';

export interface ITourDeControleProps {
  description: string;
  isDarkTheme: boolean;
  environmentMessage: string;
  hasTeamsContext: boolean;
  userDisplayName: string;
  /** Client REST du contexte SPFx — lecture des listes du site (SSO, zéro secret). */
  spHttpClient: SPHttpClient;
  /** URL absolue du site courant — base des appels `_api/web/lists`. */
  webUrl: string;
}
