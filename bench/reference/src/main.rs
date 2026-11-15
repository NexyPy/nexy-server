//! The ceiling of this machine: what hyper answers with no Python at all.
//! Usage: nexy-bench-reference <port> <threads>

use std::convert::Infallible;

use bytes::Bytes;
use http_body_util::Full;
use hyper::header::{CONTENT_TYPE, HeaderValue};
use hyper::server::conn::http1;
use hyper::service::service_fn;
use hyper::{Request, Response, StatusCode};
use hyper_util::rt::TokioIo;
use tokio::net::TcpListener;

const TEXT: &[u8] = b"Hello, World!";
const PAYLOAD: &[u8] = br#"{"message":"Hello, World!"}"#;

fn reply(body: &'static [u8], kind: &'static str) -> Response<Full<Bytes>> {
    let mut response = Response::new(Full::new(Bytes::from_static(body)));
    response.headers_mut().insert(CONTENT_TYPE, HeaderValue::from_static(kind));
    response
}

async fn answer(request: Request<hyper::body::Incoming>) -> Result<Response<Full<Bytes>>, Infallible> {
    Ok(match request.uri().path() {
        "/plaintext" => reply(TEXT, "text/plain"),
        "/payload" => reply(PAYLOAD, "application/json"),
        _ => {
            let mut response = reply(b"Not Found", "text/plain");
            *response.status_mut() = StatusCode::NOT_FOUND;
            response
        }
    })
}

async fn serve(port: u16) {
    let listener = TcpListener::bind(("127.0.0.1", port)).await.expect("bind");
    loop {
        let Ok((stream, _)) = listener.accept().await else { continue };
        let _ = stream.set_nodelay(true);
        tokio::spawn(async move {
            let io = TokioIo::new(stream);
            let _ = http1::Builder::new().serve_connection(io, service_fn(answer)).await;
        });
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let port: u16 = args.get(1).and_then(|p| p.parse().ok()).unwrap_or(8000);
    let threads: usize = args.get(2).and_then(|t| t.parse().ok()).unwrap_or(1);
    tokio::runtime::Builder::new_multi_thread()
        .worker_threads(threads)
        .enable_all()
        .build()
        .expect("runtime")
        .block_on(serve(port));
}
