# FielMedina GraphQL API Documentation

This document provides schema details and example queries for integrating the FielMedina backend into mobile applications.

## Endpoint
The GraphQL API is available at `/graphql/`.

---

## 1. Locations
Discovery points of interest (POIs).

### Type: `LocationType`
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `ID!` | Unique identifier |
| `nameEn` | `String!` | Name in English |
| `nameFr` | `String!` | Name in French |
| `latitude` | `Decimal!` | GPS Latitude |
| `longitude` | `Decimal!` | GPS Longitude |
| `storyEn` | `String!` | Description/History in English |
| `storyFr` | `String!` | Description/History in French |
| `openFrom` | `Time` | Opening time |
| `openTo` | `Time` | Closing time |
| `admissionFee` | `Decimal` | Entry fee |
| `city` | `CityType` | Associated city |
| `category` | `LocationCategoryType` | Category (e.g., Museum) |
| `images` | `[ImageLocationType!]!` | List of images |
| `closedDays` | `[WeekdayType!]!` | Days the location is closed |

---

## 2. Events
Local happenings and activities.

### Type: `EventType`
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `ID!` | Unique identifier |
| `nameEn` | `String!` | Event name (English) |
| `nameFr` | `String!` | Event name (French) |
| `startDate` | `Date!` | Event start date (ISO-8601) |
| `endDate` | `Date!` | Event end date (ISO-8601) |
| `time` | `Time!` | Event time |
| `price` | `Decimal!` | Ticket price |
| `link` | `String!` | Original booking link |
| `shortLink` | `String` | Shortened link for sharing |
| `descriptionEn` | `String!` | Detailed description (English) |
| `descriptionFr` | `String!` | Detailed description (French) |
| `city` | `CityType` | Associated city |
| `location` | `LocationType` | Specific POI venue |

---

## 3. Hikings
Guided or solo trail walks.

### Type: `HikingType`
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `ID!` | Unique identifier |
| `nameEn` | `String!` | Trail name (English) |
| `nameFr` | `String!` | Trail name (French) |
| `descriptionEn` | `String!` | Description (English) |
| `descriptionFr` | `String!` | Description (French) |
| `city` | `CityType` | Associated city |
| `locations` | `[LocationType!]!` | Ordered points of interest along the trail |
| `images` | `[ImageHikingType!]!` | List of trail images |
| `latitude` | `Decimal` | Terminus Latitude |
| `longitude` | `Decimal` | Terminus Longitude |

---

## 4. Public Transport
City and regional transit routes.

### Type: `PublicTransportNodeType`
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `ID!` | Unique identifier |
| `busNumber` | `String!` | The bus/line identifier (e.g., "Line 32") |
| `city` | `CityType` | Operating city |
| `publicTransportType` | `PublicTransportTypeType` | e.g., Bus, Train, Metro |
| `fromRegionEn / Fr` | `String` | Translated departure sub-region |
| `toRegionEn / Fr` | `String` | Translated arrival sub-region |
| `times` | `[PublicTransportTimeType!]!` | Scheduled departure times |

---

## 5. Ads
Internal advertisements for local businesses.

### Type: `AdType`
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `ID!` | Unique identifier |
| `name` | `String` | Internal campaign name |
| `link` | `String!` | Target destination URL |
| `country` | `CountryType` | Country focus for the ad |
| `city` | `CityType` | Optional city focus |
| `imageMobile` | `ImageFieldType` | Optimized image for mobile (320x50) |
| `imageTablet` | `ImageFieldType` | Optimized image for tablet (728x90) |

---

## 6. Tips
City-specific recommendations.

### Type: `TipType`
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `ID!` | Unique identifier |
| `descriptionEn` | `String!` | The tip content (English) |
| `descriptionFr` | `String!` | The tip content (French) |
| `city` | `CityType` | City the tip applies to |

---

## Example Queries

### Comprehensive City Discovery
```graphql
query DiscoverCity($cityId: Int!) {
  locations(cityId: $cityId) {
    id
    nameEn
    category { nameEn }
    images { image { url } }
  }
  events(cityId: $cityId) {
    id
    nameEn
    startDate
    price
  }
  publicTransports(cityId: $cityId) {
    busNumber
    publicTransportType { name }
    fromRegionEn
    toRegionEn
  }
  tips(cityId: $cityId) {
    descriptionEn
  }
}
```

### Hiking & Route Discovery
To retrieve a hiking trail with its **ordered locations** and **terminus geolocation**:
```graphql
query DiscoverHikes($cityId: Int!) {
  hikings(cityId: $cityId) {
    id
    nameEn
    # Terminus Geolocation
    latitude
    longitude
    # Ordered Route Checkpoints
    locations {
      id
      nameEn
      latitude
      longitude
      category { nameEn }
    }
  }
}
```

---

## Mutations

### 1. `syncUserPreference`
Used to synchronize user preferences (interests, travel companions).

**Arguments:**
- `userUid`: `UUID!`
- `firstVisit`: `Boolean!`
- `travelingWith`: `String!`
- `interests`: `[String!]!`
- `updatedAt`: `DateTime!`

**Returns:** `SyncUserPreferencePayload` (`ok: Boolean`)

**Example:**
```graphql
mutation SyncPreferences($uid: UUID!, $interests: [String!]!) {
  syncUserPreference(
    userUid: $uid,
    firstVisit: false,
    travelingWith: "friends",
    interests: $interests,
    updatedAt: "2026-01-05T08:00:00Z"
  ) {
    ok
  }
}
```

### 2. `forgetMe`
Deletes user preference data associated with a UID.

**Arguments:**
- `userUid`: `UUID!`

**Returns:** `SyncUserPreferencePayload` (`ok: Boolean`)

## Common Types

### ImageFieldType
Used for all file-based images.
- `url`: Full URL to the image.
- `width` / `height`: Dimensions.
- `name`: Clean filename.

### CityType
- `nameEn` / `nameFr`: Translated city names.
- `regionEn` / `countryEn`: Geographical context.
