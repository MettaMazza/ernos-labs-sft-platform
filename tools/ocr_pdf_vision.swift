#!/usr/bin/env swift
import AppKit
import Foundation
import PDFKit
import Vision

struct OCRLine: Codable {
    let text: String
    let confidence: Float
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

struct OCRPage: Codable {
    let page: Int
    let lines: [OCRLine]
}

struct OCRDocument: Codable {
    let schema: String
    let sourcePath: String
    let pageCount: Int
    let pages: [OCRPage]
}

guard CommandLine.arguments.count == 3 else {
    fputs("usage: ocr_pdf_vision.swift PDF OUTPUT_JSON\n", stderr)
    exit(2)
}

let source = CommandLine.arguments[1]
let output = CommandLine.arguments[2]
guard let document = PDFDocument(url: URL(fileURLWithPath: source)) else {
    fputs("unable to open PDF\n", stderr)
    exit(3)
}

var pages: [OCRPage] = []
for pageIndex in 0..<document.pageCount {
    guard let page = document.page(at: pageIndex) else { exit(4) }
    let bounds = page.bounds(for: .mediaBox)
    let image = page.thumbnail(
        of: NSSize(width: bounds.width * 4.0, height: bounds.height * 4.0),
        for: .mediaBox
    )
    var proposed = NSRect(origin: .zero, size: image.size)
    guard let cgImage = image.cgImage(forProposedRect: &proposed, context: nil, hints: nil) else { exit(5) }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.minimumTextHeight = 0.004
    try VNImageRequestHandler(cgImage: cgImage, options: [:]).perform([request])
    let observations = (request.results ?? []).sorted {
        if abs($0.boundingBox.midY - $1.boundingBox.midY) > 0.005 {
            return $0.boundingBox.midY > $1.boundingBox.midY
        }
        return $0.boundingBox.minX < $1.boundingBox.minX
    }
    let lines = observations.compactMap { observation -> OCRLine? in
        guard let candidate = observation.topCandidates(1).first else { return nil }
        let box = observation.boundingBox
        return OCRLine(
            text: candidate.string,
            confidence: candidate.confidence,
            x: box.origin.x,
            y: box.origin.y,
            width: box.size.width,
            height: box.size.height
        )
    }
    pages.append(OCRPage(page: pageIndex + 1, lines: lines))
}

let result = OCRDocument(
    schema: "sft-v3-apple-vision-ocr/1",
    sourcePath: source,
    pageCount: document.pageCount,
    pages: pages
)
let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
var data = try encoder.encode(result)
data.append(Data("\n".utf8))
try data.write(to: URL(fileURLWithPath: output), options: .atomic)
print("wrote \(output): \(document.pageCount) pages, \(pages.reduce(0) { $0 + $1.lines.count }) OCR lines")
