import React from "react";
import PlaceInformationCard from "./PlaceInformationCard";
import RouteNavigationCard from "./RouteNavigationCard";
import type { GraphNode } from "../types";

interface Props {
  navigationContext: any;
  allNodes: GraphNode[];
}

export const NavigationCard: React.FC<Props> = ({
  navigationContext,
  allNodes,
}) => {
  if (navigationContext.source) {
    return (
      <RouteNavigationCard
        navigationContext={navigationContext}
        allNodes={allNodes}
      />
    );
  }
  return (
    <PlaceInformationCard
      navigationContext={navigationContext}
      allNodes={allNodes}
    />
  );
};

export default NavigationCard;
