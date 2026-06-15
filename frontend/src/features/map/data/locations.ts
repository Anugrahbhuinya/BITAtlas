export interface CampusLocation {
  id: number;
  name: string;
  description: string;
  lat: number;
  lng: number;
}

export const locations: CampusLocation[] = [
  {
    id: 1,
    name: "CAT Hall",
    description: "CAT Hall",
    lat: 23.416,
    lng: 85.439,
  },
  {
    id: 2,
    name: "Library",
    description: "Central Library",
    lat: 23.415,
    lng: 85.44,
  },
  {
    id: 3,
    name: "Main Building",
    description: "Administrative Block",
    lat: 23.4142,
    lng: 85.4388,
  },
];
