import * as React from 'react';
import * as ReactDom from 'react-dom';
import { Version } from '@microsoft/sp-core-library';
import {
  type IPropertyPaneConfiguration,
  PropertyPaneTextField
} from '@microsoft/sp-property-pane';
import { BaseClientSideWebPart } from '@microsoft/sp-webpart-base';
import { IReadonlyTheme } from '@microsoft/sp-component-base';

import * as strings from 'TourDeControleWebPartStrings';
import TourDeControle from './components/TourDeControle';
import { ITourDeControleProps } from './components/ITourDeControleProps';

export interface ITourDeControleWebPartProps {
  description: string;
  /** Site SharePoint où vivent les listes (modele-donnees §2 bis). Vide = site courant. */
  dataSiteUrl: string;
  /** Site SharePoint des gabarits de pilotage (Contrats et administratif, §5.2). Vide = non câblé. */
  gabaritsSiteUrl: string;
  /** Chemin server-relative du dossier des gabarits actifs (`06 - Gabarit ERP`). Vide = non câblé. */
  gabaritsFolderPath: string;
  /** Chemin server-relative du classeur référentiel `T_Ressources` (audience restreinte, §5.3). Vide = non câblé. */
  referentielRessourcesPath: string;
  /** Chemin server-relative du classeur référentiel `T_Structure` (audience restreinte, §5.3). Vide = non câblé. */
  referentielStructurePath: string;
  /** Site SharePoint de la couche de saisie (Management et Gestion, §5.6). Vide = non câblé. */
  saisieSiteUrl: string;
  /** Chemin server-relative du dossier des classeurs `saisie-<code>-….xlsx`. Vide = non câblé. */
  saisieFolderPath: string;
}

export default class TourDeControleWebPart extends BaseClientSideWebPart<ITourDeControleWebPartProps> {

  private _isDarkTheme: boolean = false;
  private _environmentMessage: string = '';

  public render(): void {
    const element: React.ReactElement<ITourDeControleProps> = React.createElement(
      TourDeControle,
      {
        description: this.properties.description,
        isDarkTheme: this._isDarkTheme,
        environmentMessage: this._environmentMessage,
        hasTeamsContext: !!this.context.sdks.microsoftTeams,
        userDisplayName: this.context.pageContext.user.displayName,
        spHttpClient: this.context.spHttpClient,
        // Fabrique de client Graph (délégué, SSO) — lecture du contenu des tables (point 2).
        msGraphClientFactory: this.context.msGraphClientFactory,
        // Domicile des listes ≠ site de la page : les listes vivent sur
        // /sites/AlliaConsuling (modele-donnees §2 bis), la page cockpit peut être
        // ailleurs. Propriété configurée par le gardien ; vide = site courant.
        dataSiteUrl: (this.properties.dataSiteUrl && this.properties.dataSiteUrl.trim())
          || this.context.pageContext.web.absoluteUrl,
        // Coordonnées des gabarits (site Contrats et administratif, §5.2/§5.3) — posées
        // par le gardien (runbook, point 2). Vide = découverte non câblée → états vides honnêtes.
        gabaritsSiteUrl: (this.properties.gabaritsSiteUrl && this.properties.gabaritsSiteUrl.trim()) || '',
        gabaritsFolderPath: (this.properties.gabaritsFolderPath && this.properties.gabaritsFolderPath.trim()) || '',
        referentielRessourcesPath: (this.properties.referentielRessourcesPath && this.properties.referentielRessourcesPath.trim()) || '',
        referentielStructurePath: (this.properties.referentielStructurePath && this.properties.referentielStructurePath.trim()) || '',
        // Coordonnées de la couche de saisie (Management et Gestion, §5.6) — cible de la ligne
        // d'affectation de la cascade « Acceptée ». Vide = affectation non câblée (zéro écriture).
        saisieSiteUrl: (this.properties.saisieSiteUrl && this.properties.saisieSiteUrl.trim()) || '',
        saisieFolderPath: (this.properties.saisieFolderPath && this.properties.saisieFolderPath.trim()) || ''
      }
    );

    ReactDom.render(element, this.domElement);
  }

  protected onInit(): Promise<void> {
    return this._getEnvironmentMessage().then(message => {
      this._environmentMessage = message;
    });
  }



  private _getEnvironmentMessage(): Promise<string> {
    if (!!this.context.sdks.microsoftTeams) { // running in Teams, office.com or Outlook
      return this.context.sdks.microsoftTeams.teamsJs.app.getContext()
        .then(context => {
          let environmentMessage: string = '';
          switch (context.app.host.name) {
            case 'Office': // running in Office
              environmentMessage = this.context.isServedFromLocalhost ? strings.AppLocalEnvironmentOffice : strings.AppOfficeEnvironment;
              break;
            case 'Outlook': // running in Outlook
              environmentMessage = this.context.isServedFromLocalhost ? strings.AppLocalEnvironmentOutlook : strings.AppOutlookEnvironment;
              break;
            case 'Teams': // running in Teams
            case 'TeamsModern':
              environmentMessage = this.context.isServedFromLocalhost ? strings.AppLocalEnvironmentTeams : strings.AppTeamsTabEnvironment;
              break;
            default:
              environmentMessage = strings.UnknownEnvironment;
          }

          return environmentMessage;
        });
    }

    return Promise.resolve(this.context.isServedFromLocalhost ? strings.AppLocalEnvironmentSharePoint : strings.AppSharePointEnvironment);
  }

  protected onThemeChanged(currentTheme: IReadonlyTheme | undefined): void {
    if (!currentTheme) {
      return;
    }

    this._isDarkTheme = !!currentTheme.isInverted;
    const {
      semanticColors
    } = currentTheme;

    if (semanticColors) {
      this.domElement.style.setProperty('--bodyText', semanticColors.bodyText || null);
      this.domElement.style.setProperty('--link', semanticColors.link || null);
      this.domElement.style.setProperty('--linkHovered', semanticColors.linkHovered || null);
    }

  }

  protected onDispose(): void {
    ReactDom.unmountComponentAtNode(this.domElement);
  }

  protected get dataVersion(): Version {
    return Version.parse('1.0');
  }

  protected getPropertyPaneConfiguration(): IPropertyPaneConfiguration {
    return {
      pages: [
        {
          header: {
            description: strings.PropertyPaneDescription
          },
          groups: [
            {
              groupName: strings.BasicGroupName,
              groupFields: [
                PropertyPaneTextField('description', {
                  label: strings.DescriptionFieldLabel
                }),
                PropertyPaneTextField('dataSiteUrl', {
                  label: 'URL du site de données',
                  description: 'Site SharePoint où vivent les listes (modele-donnees §2 bis). Vide = site courant.'
                }),
                PropertyPaneTextField('gabaritsSiteUrl', {
                  label: 'URL du site des gabarits',
                  description: 'Site des gabarits de pilotage (Contrats et administratif, §5.2). Vide = non câblé.'
                }),
                PropertyPaneTextField('gabaritsFolderPath', {
                  label: 'Dossier des gabarits actifs (server-relative)',
                  description: 'Chemin du dossier « 06 - Gabarit ERP ». Vide = non câblé.'
                }),
                PropertyPaneTextField('referentielRessourcesPath', {
                  label: 'Référentiel T_Ressources (server-relative)',
                  description: 'Chemin du classeur referentiel-ressources.xlsx (audience restreinte, §5.3). Vide = non câblé.'
                }),
                PropertyPaneTextField('referentielStructurePath', {
                  label: 'Référentiel T_Structure (server-relative)',
                  description: 'Chemin du classeur referentiel-structure.xlsx (audience restreinte, §5.3). Vide = non câblé.'
                }),
                PropertyPaneTextField('saisieSiteUrl', {
                  label: 'URL du site de saisie',
                  description: 'Site de la couche de saisie (Management et Gestion, §5.6) — cible de l’affectation de la cascade « Acceptée ». Vide = non câblé.'
                }),
                PropertyPaneTextField('saisieFolderPath', {
                  label: 'Dossier des classeurs de saisie (server-relative)',
                  description: 'Chemin du dossier des « saisie-<code>-….xlsx ». Vide = non câblé.'
                })
              ]
            }
          ]
        }
      ]
    };
  }
}
