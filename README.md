# Rate Limiter v2

A configurable rate-limiter implementation for controlling request throughput and protecting services from excessive traffic.

## Overview

This project provides a reusable rate-limiting component that can be used to enforce request quotas over a defined time window. Configure the allowed request count and window duration to match your application's traffic requirements.

## Features

- Configurable request limits
- Fixed time-window enforcement
- Easy integration into applications and APIs
- Protection against traffic spikes and abusive request patterns

## Getting Started

### Prerequisites

- A supported runtime or package manager for this project
- (Optional) A running application or API to integrate with

### Installation

Clone the repository and follow the setup instructions below:

```bash
git clone https://github.com/premshscaler/Rate-Limiter-v2.git
cd Rate-Limiter-v2
```

Install dependencies and run the project using the commands used by the repository's implementation (for example, package-manager or build commands).

## Usage

Configure the maximum number of requests and the time window, then apply the limiter to each incoming request or request source.

Example configuration:

```text
Limit: 100 requests
Window: 60 seconds
```

When the limit is exceeded, the limiter should reject or delay the request until the current window resets.

## Configuration

| Option | Description | Example |
|---|---|---|
| `limit` | Maximum requests allowed in a window | `100` |
| `window` | Duration of each rate-limit window | `60s` |
| `key` | Identifier used to track requests | user ID or IP address |

## Error Handling

Requests exceeding the configured quota can return an HTTP-style response such as:

```text
Status: 429 Too Many Requests
Retry-After: <seconds until reset>
```

## Testing

Run the repository's test command after completing setup. Add tests for:

- Requests below the configured limit
- The first request that exceeds the limit
- Window reset behavior
- Independent limits for different keys
- Concurrent requests

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a pull request.

## License

Add a license for this project if you plan to distribute it publicly.
