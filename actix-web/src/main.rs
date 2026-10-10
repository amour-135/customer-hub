use serde::Serialize;
use worker::*;

#[derive(Serialize)]
struct DataItem {
    id: u32,
    name: String,
    value: u32,
}

#[derive(Serialize)]
struct DataResponse {
    data: Vec<DataItem>,
    total: usize,
    timestamp: String,
}

#[event(fetch)]
pub async fn main(req: Request, _env: Env, _ctx: Context) -> Result<Response> {
    let path = req.path();

    let (status, content_type, body) = match path {
        "/" | "/index.html" => {
            let html = include_str!("../public/index.html");
            (200, "text/html; charset=utf-8", html.to_string())
        }
        "/favicon.ico" => {
            let favicon = include_bytes!("../public/favicon.ico");
            return Response::from_bytes(favicon.to_vec())
                .with_header("Content-Type", "image/x-icon");
        }
        "/api/data" => {
            let items = vec![
                DataItem { id: 1, name: "Sample Item 1".into(), value: 100 },
                DataItem { id: 2, name: "Sample Item 2".into(), value: 200 },
                DataItem { id: 3, name: "Sample Item 3".into(), value: 300 },
            ];
            let resp = DataResponse {
                total: items.len(),
                data: items,
                timestamp: "2024-01-01T00:00:00Z".into(),
            };
            (200, "application/json", serde_json::to_string(&resp).unwrap())
        }
        _ => {
            let html = include_str!("../public/index.html");
            (200, "text/html; charset=utf-8", html.to_string())
        }
    };

    Response::ok(body)
        .with_status(status)
        .with_header("Content-Type", content_type)
}
