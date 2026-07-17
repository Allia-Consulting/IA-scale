import type { SPHttpClient, MSGraphClientFactory } from '@microsoft/sp-http';

export interface ITourDeControleProps {
  description: string;
  isDarkTheme: boolean;
  environmentMessage: string;
  hasTeamsContext: boolean;
  userDisplayName: string;
  /** Client REST du contexte SPFx — lecture des listes du site (SSO, zéro secret). */
  spHttpClient: SPHttpClient;
  /**
   * Fabrique de client Microsoft Graph (délégué, SSO SPFx) — lecture du CONTENU des tables des
   * gabarits + référentiel via l'API Workbook (point 2, permission Sites.Read.All). Zéro secret.
   */
  msGraphClientFactory: MSGraphClientFactory;
  /**
   * URL absolue du site où vivent les listes (modele-donnees §2 bis) — base des
   * appels `_api/web/lists`. Peut différer du site de la page (défaut = site courant).
   */
  dataSiteUrl: string;
  /**
   * URL absolue du site des gabarits de pilotage (Contrats et administratif,
   * modele-donnees §5.2). Vide = découverte non câblée (états vides honnêtes).
   */
  gabaritsSiteUrl: string;
  /** Chemin server-relative du dossier des gabarits actifs (`06 - Gabarit ERP`). Vide = non câblé. */
  gabaritsFolderPath: string;
  /** Chemin server-relative du classeur référentiel `T_Ressources` (audience restreinte, §5.3). Vide = non câblé. */
  referentielRessourcesPath: string;
  /** Chemin server-relative du classeur référentiel `T_Structure` (audience restreinte, §5.3). Vide = non câblé. */
  referentielStructurePath: string;
}
