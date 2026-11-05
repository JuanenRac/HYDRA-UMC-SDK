// Generated from the HYDRA-UMC JSON Schemas by tools/generate_types.py. Do not edit.
// ignore_for_file: non_constant_identifier_names, constant_identifier_names

class CanaryDeployResult {
  final String? schema_version;
  final String deployId;
  final String proposalId;
  final String projectName;
  final String startedAt;
  final String finishedAt;
  final bool promoted;
  final String stageReached;
  final String buildOutput;
  final String detail;
  final String? backupPath;
  final String? patchPath;
  const CanaryDeployResult({this.schema_version, required this.deployId, required this.proposalId, required this.projectName, required this.startedAt, required this.finishedAt, required this.promoted, required this.stageReached, required this.buildOutput, required this.detail, this.backupPath, this.patchPath});
  factory CanaryDeployResult.fromJson(Map<String, dynamic> json) => CanaryDeployResult(
        schema_version: json["schema_version"] == null ? null : json["schema_version"] as String,
        deployId: json["deployId"] as String,
        proposalId: json["proposalId"] as String,
        projectName: json["projectName"] as String,
        startedAt: json["startedAt"] as String,
        finishedAt: json["finishedAt"] as String,
        promoted: json["promoted"] as bool,
        stageReached: json["stageReached"] as String,
        buildOutput: json["buildOutput"] as String,
        detail: json["detail"] as String,
        backupPath: json["backupPath"] == null ? null : json["backupPath"] as String,
        patchPath: json["patchPath"] == null ? null : json["patchPath"] as String,
      );
  Map<String, dynamic> toJson() => {
        if (schema_version != null) "schema_version": schema_version,
        "deployId": deployId,
        "proposalId": proposalId,
        "projectName": projectName,
        "startedAt": startedAt,
        "finishedAt": finishedAt,
        "promoted": promoted,
        "stageReached": stageReached,
        "buildOutput": buildOutput,
        "detail": detail,
        if (backupPath != null) "backupPath": backupPath,
        if (patchPath != null) "patchPath": patchPath,
      };
}

class Capability {
  final String schema_version;
  final CapabilityTarget target;
  final String kind;
  final bool declared;
  final String? last_checked_at_utc;
  final String? checked_configuration;
  final double? max_age_seconds;
  final String? last_check_outcome;
  final String? last_check_reason;
  const Capability({required this.schema_version, required this.target, required this.kind, required this.declared, this.last_checked_at_utc, this.checked_configuration, this.max_age_seconds, this.last_check_outcome, this.last_check_reason});
  factory Capability.fromJson(Map<String, dynamic> json) => Capability(
        schema_version: json["schema_version"] as String,
        target: CapabilityTarget.fromJson(Map<String, dynamic>.from(json["target"] as Map)),
        kind: json["kind"] as String,
        declared: json["declared"] as bool,
        last_checked_at_utc: json["last_checked_at_utc"] == null ? null : json["last_checked_at_utc"] as String,
        checked_configuration: json["checked_configuration"] == null ? null : json["checked_configuration"] as String,
        max_age_seconds: json["max_age_seconds"] == null ? null : (json["max_age_seconds"] as num).toDouble(),
        last_check_outcome: json["last_check_outcome"] == null ? null : json["last_check_outcome"] as String,
        last_check_reason: json["last_check_reason"] == null ? null : json["last_check_reason"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "target": target.toJson(),
        "kind": kind,
        "declared": declared,
        if (last_checked_at_utc != null) "last_checked_at_utc": last_checked_at_utc,
        if (checked_configuration != null) "checked_configuration": checked_configuration,
        if (max_age_seconds != null) "max_age_seconds": max_age_seconds,
        if (last_check_outcome != null) "last_check_outcome": last_check_outcome,
        if (last_check_reason != null) "last_check_reason": last_check_reason,
      };
}

class CapabilityTarget {
  final String kind;
  final String id;
  const CapabilityTarget({required this.kind, required this.id});
  factory CapabilityTarget.fromJson(Map<String, dynamic> json) => CapabilityTarget(
        kind: json["kind"] as String,
        id: json["id"] as String,
      );
  Map<String, dynamic> toJson() => {
        "kind": kind,
        "id": id,
      };
}

class ChangeProposal {
  final String? schema_version;
  final String proposalId;
  final String incidentId;
  final String correlationId;
  final String createdAt;
  final String projectName;
  final String description;
  final String diff;
  final String rationale;
  final String status;
  final String? decidedBy;
  final String? decidedAt;
  final String? decisionReason;
  final String? approvedContentDigest;
  final bool? allowProtectedPaths;
  final String? approvalExpiresAt;
  final String? approvedBaseCommit;
  final String? approvalSignature;
  final String? generatedBy;
  const ChangeProposal({this.schema_version, required this.proposalId, required this.incidentId, required this.correlationId, required this.createdAt, required this.projectName, required this.description, required this.diff, required this.rationale, required this.status, this.decidedBy, this.decidedAt, this.decisionReason, this.approvedContentDigest, this.allowProtectedPaths, this.approvalExpiresAt, this.approvedBaseCommit, this.approvalSignature, this.generatedBy});
  factory ChangeProposal.fromJson(Map<String, dynamic> json) => ChangeProposal(
        schema_version: json["schema_version"] == null ? null : json["schema_version"] as String,
        proposalId: json["proposalId"] as String,
        incidentId: json["incidentId"] as String,
        correlationId: json["correlationId"] as String,
        createdAt: json["createdAt"] as String,
        projectName: json["projectName"] as String,
        description: json["description"] as String,
        diff: json["diff"] as String,
        rationale: json["rationale"] as String,
        status: json["status"] as String,
        decidedBy: json["decidedBy"] == null ? null : json["decidedBy"] as String,
        decidedAt: json["decidedAt"] == null ? null : json["decidedAt"] as String,
        decisionReason: json["decisionReason"] == null ? null : json["decisionReason"] as String,
        approvedContentDigest: json["approvedContentDigest"] == null ? null : json["approvedContentDigest"] as String,
        allowProtectedPaths: json["allowProtectedPaths"] == null ? null : json["allowProtectedPaths"] as bool,
        approvalExpiresAt: json["approvalExpiresAt"] == null ? null : json["approvalExpiresAt"] as String,
        approvedBaseCommit: json["approvedBaseCommit"] == null ? null : json["approvedBaseCommit"] as String,
        approvalSignature: json["approvalSignature"] == null ? null : json["approvalSignature"] as String,
        generatedBy: json["generatedBy"] == null ? null : json["generatedBy"] as String,
      );
  Map<String, dynamic> toJson() => {
        if (schema_version != null) "schema_version": schema_version,
        "proposalId": proposalId,
        "incidentId": incidentId,
        "correlationId": correlationId,
        "createdAt": createdAt,
        "projectName": projectName,
        "description": description,
        "diff": diff,
        "rationale": rationale,
        "status": status,
        if (decidedBy != null) "decidedBy": decidedBy,
        if (decidedAt != null) "decidedAt": decidedAt,
        if (decisionReason != null) "decisionReason": decisionReason,
        if (approvedContentDigest != null) "approvedContentDigest": approvedContentDigest,
        if (allowProtectedPaths != null) "allowProtectedPaths": allowProtectedPaths,
        if (approvalExpiresAt != null) "approvalExpiresAt": approvalExpiresAt,
        if (approvedBaseCommit != null) "approvedBaseCommit": approvedBaseCommit,
        if (approvalSignature != null) "approvalSignature": approvalSignature,
        if (generatedBy != null) "generatedBy": generatedBy,
      };
}

class CommandLifecycleEvent {
  final String schema_version;
  final String operation_id;
  final String robot_id;
  final String command;
  final String state;
  final String at_utc;
  final int sequence;
  final String? reason;
  const CommandLifecycleEvent({required this.schema_version, required this.operation_id, required this.robot_id, required this.command, required this.state, required this.at_utc, required this.sequence, this.reason});
  factory CommandLifecycleEvent.fromJson(Map<String, dynamic> json) => CommandLifecycleEvent(
        schema_version: json["schema_version"] as String,
        operation_id: json["operation_id"] as String,
        robot_id: json["robot_id"] as String,
        command: json["command"] as String,
        state: json["state"] as String,
        at_utc: json["at_utc"] as String,
        sequence: (json["sequence"] as num).toInt(),
        reason: json["reason"] == null ? null : json["reason"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "operation_id": operation_id,
        "robot_id": robot_id,
        "command": command,
        "state": state,
        "at_utc": at_utc,
        "sequence": sequence,
        if (reason != null) "reason": reason,
      };
}

class ConnectionClient {
  final String schema_version;
  final String id;
  final String kind;
  final String? user;
  final String? app_version;
  final String? origin;
  final bool? two_factor;
  final String first_seen_utc;
  final String last_seen_utc;
  final String? last_failure_utc;
  final int active_sessions;
  final int logins_ok;
  final int logins_failed;
  final String? ip;
  final String? agent;
  const ConnectionClient({required this.schema_version, required this.id, required this.kind, this.user, this.app_version, this.origin, this.two_factor, required this.first_seen_utc, required this.last_seen_utc, this.last_failure_utc, required this.active_sessions, required this.logins_ok, required this.logins_failed, this.ip, this.agent});
  factory ConnectionClient.fromJson(Map<String, dynamic> json) => ConnectionClient(
        schema_version: json["schema_version"] as String,
        id: json["id"] as String,
        kind: json["kind"] as String,
        user: json["user"] == null ? null : json["user"] as String,
        app_version: json["app_version"] == null ? null : json["app_version"] as String,
        origin: json["origin"] == null ? null : json["origin"] as String,
        two_factor: json["two_factor"] == null ? null : json["two_factor"] as bool,
        first_seen_utc: json["first_seen_utc"] as String,
        last_seen_utc: json["last_seen_utc"] as String,
        last_failure_utc: json["last_failure_utc"] == null ? null : json["last_failure_utc"] as String,
        active_sessions: (json["active_sessions"] as num).toInt(),
        logins_ok: (json["logins_ok"] as num).toInt(),
        logins_failed: (json["logins_failed"] as num).toInt(),
        ip: json["ip"] == null ? null : json["ip"] as String,
        agent: json["agent"] == null ? null : json["agent"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "id": id,
        "kind": kind,
        if (user != null) "user": user,
        if (app_version != null) "app_version": app_version,
        if (origin != null) "origin": origin,
        if (two_factor != null) "two_factor": two_factor,
        "first_seen_utc": first_seen_utc,
        "last_seen_utc": last_seen_utc,
        if (last_failure_utc != null) "last_failure_utc": last_failure_utc,
        "active_sessions": active_sessions,
        "logins_ok": logins_ok,
        "logins_failed": logins_failed,
        if (ip != null) "ip": ip,
        if (agent != null) "agent": agent,
      };
}

class ConnectionEvent {
  final String schema_version;
  final int id;
  final String at_utc;
  final String action;
  final String client_kind;
  final String client_id;
  final String? user;
  final String? origin;
  final bool? two_factor;
  final String? app_version;
  final String? ip;
  final String? agent;
  const ConnectionEvent({required this.schema_version, required this.id, required this.at_utc, required this.action, required this.client_kind, required this.client_id, this.user, this.origin, this.two_factor, this.app_version, this.ip, this.agent});
  factory ConnectionEvent.fromJson(Map<String, dynamic> json) => ConnectionEvent(
        schema_version: json["schema_version"] as String,
        id: (json["id"] as num).toInt(),
        at_utc: json["at_utc"] as String,
        action: json["action"] as String,
        client_kind: json["client_kind"] as String,
        client_id: json["client_id"] as String,
        user: json["user"] == null ? null : json["user"] as String,
        origin: json["origin"] == null ? null : json["origin"] as String,
        two_factor: json["two_factor"] == null ? null : json["two_factor"] as bool,
        app_version: json["app_version"] == null ? null : json["app_version"] as String,
        ip: json["ip"] == null ? null : json["ip"] as String,
        agent: json["agent"] == null ? null : json["agent"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "id": id,
        "at_utc": at_utc,
        "action": action,
        "client_kind": client_kind,
        "client_id": client_id,
        if (user != null) "user": user,
        if (origin != null) "origin": origin,
        if (two_factor != null) "two_factor": two_factor,
        if (app_version != null) "app_version": app_version,
        if (ip != null) "ip": ip,
        if (agent != null) "agent": agent,
      };
}

class DetectionFrame {
  final String schema_version;
  final String frame_id;
  final String capture_ts_utc;
  final String box_unit;
  final List<DetectionFrameDetections> detections;
  final String? session_id;
  final DetectionFrameModel? model;
  const DetectionFrame({required this.schema_version, required this.frame_id, required this.capture_ts_utc, required this.box_unit, required this.detections, this.session_id, this.model});
  factory DetectionFrame.fromJson(Map<String, dynamic> json) => DetectionFrame(
        schema_version: json["schema_version"] as String,
        frame_id: json["frame_id"] as String,
        capture_ts_utc: json["capture_ts_utc"] as String,
        box_unit: json["box_unit"] as String,
        detections: (json["detections"] as List).map((e0) => DetectionFrameDetections.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
        session_id: json["session_id"] == null ? null : json["session_id"] as String,
        model: json["model"] == null ? null : DetectionFrameModel.fromJson(Map<String, dynamic>.from(json["model"] as Map)),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "frame_id": frame_id,
        "capture_ts_utc": capture_ts_utc,
        "box_unit": box_unit,
        "detections": detections.map((e0) => e0.toJson()).toList(),
        if (session_id != null) "session_id": session_id,
        if (model != null) "model": model!.toJson(),
      };
}

class DetectionFrameDetections {
  final int class_id;
  final String label;
  final double score;
  final DetectionFrameDetectionsBox box;
  const DetectionFrameDetections({required this.class_id, required this.label, required this.score, required this.box});
  factory DetectionFrameDetections.fromJson(Map<String, dynamic> json) => DetectionFrameDetections(
        class_id: (json["class_id"] as num).toInt(),
        label: json["label"] as String,
        score: (json["score"] as num).toDouble(),
        box: DetectionFrameDetectionsBox.fromJson(Map<String, dynamic>.from(json["box"] as Map)),
      );
  Map<String, dynamic> toJson() => {
        "class_id": class_id,
        "label": label,
        "score": score,
        "box": box.toJson(),
      };
}

class DetectionFrameDetectionsBox {
  final double x_min;
  final double y_min;
  final double x_max;
  final double y_max;
  const DetectionFrameDetectionsBox({required this.x_min, required this.y_min, required this.x_max, required this.y_max});
  factory DetectionFrameDetectionsBox.fromJson(Map<String, dynamic> json) => DetectionFrameDetectionsBox(
        x_min: (json["x_min"] as num).toDouble(),
        y_min: (json["y_min"] as num).toDouble(),
        x_max: (json["x_max"] as num).toDouble(),
        y_max: (json["y_max"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "x_min": x_min,
        "y_min": y_min,
        "x_max": x_max,
        "y_max": y_max,
      };
}

class DetectionFrameModel {
  final String model_name;
  final String model_version;
  final String model_sha256;
  final String hailo_arch;
  final String pipeline_version;
  const DetectionFrameModel({required this.model_name, required this.model_version, required this.model_sha256, required this.hailo_arch, required this.pipeline_version});
  factory DetectionFrameModel.fromJson(Map<String, dynamic> json) => DetectionFrameModel(
        model_name: json["model_name"] as String,
        model_version: json["model_version"] as String,
        model_sha256: json["model_sha256"] as String,
        hailo_arch: json["hailo_arch"] as String,
        pipeline_version: json["pipeline_version"] as String,
      );
  Map<String, dynamic> toJson() => {
        "model_name": model_name,
        "model_version": model_version,
        "model_sha256": model_sha256,
        "hailo_arch": hailo_arch,
        "pipeline_version": pipeline_version,
      };
}

class DeviceDescriptor {
  final String schema_version;
  final String node_id;
  final String profile;
  final String hostname;
  final String machine;
  final String operating_system;
  final String kernel;
  final List<String> interfaces;
  const DeviceDescriptor({required this.schema_version, required this.node_id, required this.profile, required this.hostname, required this.machine, required this.operating_system, required this.kernel, required this.interfaces});
  factory DeviceDescriptor.fromJson(Map<String, dynamic> json) => DeviceDescriptor(
        schema_version: json["schema_version"] as String,
        node_id: json["node_id"] as String,
        profile: json["profile"] as String,
        hostname: json["hostname"] as String,
        machine: json["machine"] as String,
        operating_system: json["operating_system"] as String,
        kernel: json["kernel"] as String,
        interfaces: (json["interfaces"] as List).map((e0) => e0 as String).toList(),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "node_id": node_id,
        "profile": profile,
        "hostname": hostname,
        "machine": machine,
        "operating_system": operating_system,
        "kernel": kernel,
        "interfaces": interfaces,
      };
}

class EcosystemHealth {
  final String schema_version;
  final String generated_at_utc;
  final bool available;
  final EcosystemHealthSummary summary;
  final List<EcosystemHealthServices> services;
  final Object? certificate;
  final List<EcosystemHealthWarnings> warnings;
  const EcosystemHealth({required this.schema_version, required this.generated_at_utc, required this.available, required this.summary, required this.services, this.certificate, required this.warnings});
  factory EcosystemHealth.fromJson(Map<String, dynamic> json) => EcosystemHealth(
        schema_version: json["schema_version"] as String,
        generated_at_utc: json["generated_at_utc"] as String,
        available: json["available"] as bool,
        summary: EcosystemHealthSummary.fromJson(Map<String, dynamic>.from(json["summary"] as Map)),
        services: (json["services"] as List).map((e0) => EcosystemHealthServices.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
        certificate: json["certificate"],
        warnings: (json["warnings"] as List).map((e0) => EcosystemHealthWarnings.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "generated_at_utc": generated_at_utc,
        "available": available,
        "summary": summary.toJson(),
        "services": services.map((e0) => e0.toJson()).toList(),
        "certificate": certificate,
        "warnings": warnings.map((e0) => e0.toJson()).toList(),
      };
}

class EcosystemHealthSummary {
  final int total;
  final int ok;
  final int degraded;
  final int down;
  final int unknown;
  final int drift;
  const EcosystemHealthSummary({required this.total, required this.ok, required this.degraded, required this.down, required this.unknown, required this.drift});
  factory EcosystemHealthSummary.fromJson(Map<String, dynamic> json) => EcosystemHealthSummary(
        total: (json["total"] as num).toInt(),
        ok: (json["ok"] as num).toInt(),
        degraded: (json["degraded"] as num).toInt(),
        down: (json["down"] as num).toInt(),
        unknown: (json["unknown"] as num).toInt(),
        drift: (json["drift"] as num).toInt(),
      );
  Map<String, dynamic> toJson() => {
        "total": total,
        "ok": ok,
        "degraded": degraded,
        "down": down,
        "unknown": unknown,
        "drift": drift,
      };
}

class EcosystemHealthServices {
  final String name;
  final Object? family;
  final Object? role;
  final String state;
  final String reason;
  final Object? version_expected;
  final Object? version_reported;
  final bool drift;
  final Object? last_seen_utc;
  final Object? latency_ms;
  final Object? port;
  final Object? health_path;
  final Object? systemd_unit;
  final Object? active_state;
  const EcosystemHealthServices({required this.name, this.family, this.role, required this.state, required this.reason, this.version_expected, this.version_reported, required this.drift, this.last_seen_utc, this.latency_ms, this.port, this.health_path, this.systemd_unit, this.active_state});
  factory EcosystemHealthServices.fromJson(Map<String, dynamic> json) => EcosystemHealthServices(
        name: json["name"] as String,
        family: json["family"],
        role: json["role"],
        state: json["state"] as String,
        reason: json["reason"] as String,
        version_expected: json["version_expected"],
        version_reported: json["version_reported"],
        drift: json["drift"] as bool,
        last_seen_utc: json["last_seen_utc"],
        latency_ms: json["latency_ms"],
        port: json["port"],
        health_path: json["health_path"],
        systemd_unit: json["systemd_unit"],
        active_state: json["active_state"],
      );
  Map<String, dynamic> toJson() => {
        "name": name,
        "family": family,
        "role": role,
        "state": state,
        "reason": reason,
        "version_expected": version_expected,
        "version_reported": version_reported,
        "drift": drift,
        "last_seen_utc": last_seen_utc,
        "latency_ms": latency_ms,
        if (port != null) "port": port,
        if (health_path != null) "health_path": health_path,
        if (systemd_unit != null) "systemd_unit": systemd_unit,
        if (active_state != null) "active_state": active_state,
      };
}

class EcosystemHealthWarnings {
  final String code;
  final String? service;
  const EcosystemHealthWarnings({required this.code, this.service});
  factory EcosystemHealthWarnings.fromJson(Map<String, dynamic> json) => EcosystemHealthWarnings(
        code: json["code"] as String,
        service: json["service"] == null ? null : json["service"] as String,
      );
  Map<String, dynamic> toJson() => {
        "code": code,
        if (service != null) "service": service,
      };
}

class EventEnvelope {
  final String schema_version;
  final String event_id;
  final String type;
  final String source;
  final String timestamp_utc;
  final int sequence;
  final String? correlation_id;
  const EventEnvelope({required this.schema_version, required this.event_id, required this.type, required this.source, required this.timestamp_utc, required this.sequence, this.correlation_id});
  factory EventEnvelope.fromJson(Map<String, dynamic> json) => EventEnvelope(
        schema_version: json["schema_version"] as String,
        event_id: json["event_id"] as String,
        type: json["type"] as String,
        source: json["source"] as String,
        timestamp_utc: json["timestamp_utc"] as String,
        sequence: (json["sequence"] as num).toInt(),
        correlation_id: json["correlation_id"] == null ? null : json["correlation_id"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "event_id": event_id,
        "type": type,
        "source": source,
        "timestamp_utc": timestamp_utc,
        "sequence": sequence,
        if (correlation_id != null) "correlation_id": correlation_id,
      };
}

class FrameMeta {
  final String schema_version;
  final String frame_id;
  final String capture_ts_utc;
  final int width;
  final int height;
  final String pixel_format;
  final String? session_id;
  final String? source_id;
  final int? stride;
  final int? sequence;
  const FrameMeta({required this.schema_version, required this.frame_id, required this.capture_ts_utc, required this.width, required this.height, required this.pixel_format, this.session_id, this.source_id, this.stride, this.sequence});
  factory FrameMeta.fromJson(Map<String, dynamic> json) => FrameMeta(
        schema_version: json["schema_version"] as String,
        frame_id: json["frame_id"] as String,
        capture_ts_utc: json["capture_ts_utc"] as String,
        width: (json["width"] as num).toInt(),
        height: (json["height"] as num).toInt(),
        pixel_format: json["pixel_format"] as String,
        session_id: json["session_id"] == null ? null : json["session_id"] as String,
        source_id: json["source_id"] == null ? null : json["source_id"] as String,
        stride: json["stride"] == null ? null : (json["stride"] as num).toInt(),
        sequence: json["sequence"] == null ? null : (json["sequence"] as num).toInt(),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "frame_id": frame_id,
        "capture_ts_utc": capture_ts_utc,
        "width": width,
        "height": height,
        "pixel_format": pixel_format,
        if (session_id != null) "session_id": session_id,
        if (source_id != null) "source_id": source_id,
        if (stride != null) "stride": stride,
        if (sequence != null) "sequence": sequence,
      };
}

class HealthReport {
  final String schema_version;
  final String state;
  final String timestamp_utc;
  final Map<String, Object?> checks;
  const HealthReport({required this.schema_version, required this.state, required this.timestamp_utc, required this.checks});
  factory HealthReport.fromJson(Map<String, dynamic> json) => HealthReport(
        schema_version: json["schema_version"] as String,
        state: json["state"] as String,
        timestamp_utc: json["timestamp_utc"] as String,
        checks: Map<String, dynamic>.from(json["checks"] as Map),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "state": state,
        "timestamp_utc": timestamp_utc,
        "checks": checks,
      };
}

class MaintenanceIncident {
  final String? schema_version;
  final String incidentId;
  final String sourceNode;
  final String detectedAt;
  final String severity;
  final String component;
  final String symptom;
  final List<String> evidenceRefs;
  final String redactionLevel;
  final String? requestedBy;
  final String correlationId;
  const MaintenanceIncident({this.schema_version, required this.incidentId, required this.sourceNode, required this.detectedAt, required this.severity, required this.component, required this.symptom, required this.evidenceRefs, required this.redactionLevel, this.requestedBy, required this.correlationId});
  factory MaintenanceIncident.fromJson(Map<String, dynamic> json) => MaintenanceIncident(
        schema_version: json["schema_version"] == null ? null : json["schema_version"] as String,
        incidentId: json["incidentId"] as String,
        sourceNode: json["sourceNode"] as String,
        detectedAt: json["detectedAt"] as String,
        severity: json["severity"] as String,
        component: json["component"] as String,
        symptom: json["symptom"] as String,
        evidenceRefs: (json["evidenceRefs"] as List).map((e0) => e0 as String).toList(),
        redactionLevel: json["redactionLevel"] as String,
        requestedBy: json["requestedBy"] == null ? null : json["requestedBy"] as String,
        correlationId: json["correlationId"] as String,
      );
  Map<String, dynamic> toJson() => {
        if (schema_version != null) "schema_version": schema_version,
        "incidentId": incidentId,
        "sourceNode": sourceNode,
        "detectedAt": detectedAt,
        "severity": severity,
        "component": component,
        "symptom": symptom,
        "evidenceRefs": evidenceRefs,
        "redactionLevel": redactionLevel,
        if (requestedBy != null) "requestedBy": requestedBy,
        "correlationId": correlationId,
      };
}

class NodeSnapshot {
  final String? schema_version;
  final String sourceNode;
  final String collectedAt;
  final String correlationId;
  final List<NodeSnapshotProjects> projects;
  final List<NodeSnapshotManifestIssues> manifestIssues;
  final bool? systemdAvailable;
  final String? systemdUnavailableReason;
  final List<NodeSnapshotServiceHealth> serviceHealth;
  final List<NodeSnapshotHttpHealth> httpHealth;
  final List<NodeSnapshotIncidents> incidents;
  final NodeSnapshotHostHealth? hostHealth;
  const NodeSnapshot({this.schema_version, required this.sourceNode, required this.collectedAt, required this.correlationId, required this.projects, required this.manifestIssues, this.systemdAvailable, this.systemdUnavailableReason, required this.serviceHealth, required this.httpHealth, required this.incidents, this.hostHealth});
  factory NodeSnapshot.fromJson(Map<String, dynamic> json) => NodeSnapshot(
        schema_version: json["schema_version"] == null ? null : json["schema_version"] as String,
        sourceNode: json["sourceNode"] as String,
        collectedAt: json["collectedAt"] as String,
        correlationId: json["correlationId"] as String,
        projects: (json["projects"] as List).map((e0) => NodeSnapshotProjects.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
        manifestIssues: (json["manifestIssues"] as List).map((e0) => NodeSnapshotManifestIssues.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
        systemdAvailable: json["systemdAvailable"] == null ? null : json["systemdAvailable"] as bool,
        systemdUnavailableReason: json["systemdUnavailableReason"] == null ? null : json["systemdUnavailableReason"] as String,
        serviceHealth: (json["serviceHealth"] as List).map((e0) => NodeSnapshotServiceHealth.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
        httpHealth: (json["httpHealth"] as List).map((e0) => NodeSnapshotHttpHealth.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
        incidents: (json["incidents"] as List).map((e0) => NodeSnapshotIncidents.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
        hostHealth: json["hostHealth"] == null ? null : NodeSnapshotHostHealth.fromJson(Map<String, dynamic>.from(json["hostHealth"] as Map)),
      );
  Map<String, dynamic> toJson() => {
        if (schema_version != null) "schema_version": schema_version,
        "sourceNode": sourceNode,
        "collectedAt": collectedAt,
        "correlationId": correlationId,
        "projects": projects.map((e0) => e0.toJson()).toList(),
        "manifestIssues": manifestIssues.map((e0) => e0.toJson()).toList(),
        if (systemdAvailable != null) "systemdAvailable": systemdAvailable,
        if (systemdUnavailableReason != null) "systemdUnavailableReason": systemdUnavailableReason,
        "serviceHealth": serviceHealth.map((e0) => e0.toJson()).toList(),
        "httpHealth": httpHealth.map((e0) => e0.toJson()).toList(),
        "incidents": incidents.map((e0) => e0.toJson()).toList(),
        if (hostHealth != null) "hostHealth": hostHealth!.toJson(),
      };
}

class NodeSnapshotProjects {
  final String name;
  final String version;
  final String maturity;
  final String manifestPath;
  const NodeSnapshotProjects({required this.name, required this.version, required this.maturity, required this.manifestPath});
  factory NodeSnapshotProjects.fromJson(Map<String, dynamic> json) => NodeSnapshotProjects(
        name: json["name"] as String,
        version: json["version"] as String,
        maturity: json["maturity"] as String,
        manifestPath: json["manifestPath"] as String,
      );
  Map<String, dynamic> toJson() => {
        "name": name,
        "version": version,
        "maturity": maturity,
        "manifestPath": manifestPath,
      };
}

class NodeSnapshotManifestIssues {
  final String path;
  final String reason;
  const NodeSnapshotManifestIssues({required this.path, required this.reason});
  factory NodeSnapshotManifestIssues.fromJson(Map<String, dynamic> json) => NodeSnapshotManifestIssues(
        path: json["path"] as String,
        reason: json["reason"] as String,
      );
  Map<String, dynamic> toJson() => {
        "path": path,
        "reason": reason,
      };
}

class NodeSnapshotServiceHealth {
  final String unitName;
  final bool active;
  final String detail;
  const NodeSnapshotServiceHealth({required this.unitName, required this.active, required this.detail});
  factory NodeSnapshotServiceHealth.fromJson(Map<String, dynamic> json) => NodeSnapshotServiceHealth(
        unitName: json["unitName"] as String,
        active: json["active"] as bool,
        detail: json["detail"] as String,
      );
  Map<String, dynamic> toJson() => {
        "unitName": unitName,
        "active": active,
        "detail": detail,
      };
}

class NodeSnapshotHttpHealth {
  final String url;
  final bool reachable;
  final int? statusCode;
  final String detail;
  const NodeSnapshotHttpHealth({required this.url, required this.reachable, this.statusCode, required this.detail});
  factory NodeSnapshotHttpHealth.fromJson(Map<String, dynamic> json) => NodeSnapshotHttpHealth(
        url: json["url"] as String,
        reachable: json["reachable"] as bool,
        statusCode: json["statusCode"] == null ? null : (json["statusCode"] as num).toInt(),
        detail: json["detail"] as String,
      );
  Map<String, dynamic> toJson() => {
        "url": url,
        "reachable": reachable,
        if (statusCode != null) "statusCode": statusCode,
        "detail": detail,
      };
}

class NodeSnapshotIncidents {
  final String? schema_version;
  final String incidentId;
  final String sourceNode;
  final String detectedAt;
  final String severity;
  final String component;
  final String symptom;
  final List<String> evidenceRefs;
  final String redactionLevel;
  final String? requestedBy;
  final String correlationId;
  const NodeSnapshotIncidents({this.schema_version, required this.incidentId, required this.sourceNode, required this.detectedAt, required this.severity, required this.component, required this.symptom, required this.evidenceRefs, required this.redactionLevel, this.requestedBy, required this.correlationId});
  factory NodeSnapshotIncidents.fromJson(Map<String, dynamic> json) => NodeSnapshotIncidents(
        schema_version: json["schema_version"] == null ? null : json["schema_version"] as String,
        incidentId: json["incidentId"] as String,
        sourceNode: json["sourceNode"] as String,
        detectedAt: json["detectedAt"] as String,
        severity: json["severity"] as String,
        component: json["component"] as String,
        symptom: json["symptom"] as String,
        evidenceRefs: (json["evidenceRefs"] as List).map((e0) => e0 as String).toList(),
        redactionLevel: json["redactionLevel"] as String,
        requestedBy: json["requestedBy"] == null ? null : json["requestedBy"] as String,
        correlationId: json["correlationId"] as String,
      );
  Map<String, dynamic> toJson() => {
        if (schema_version != null) "schema_version": schema_version,
        "incidentId": incidentId,
        "sourceNode": sourceNode,
        "detectedAt": detectedAt,
        "severity": severity,
        "component": component,
        "symptom": symptom,
        "evidenceRefs": evidenceRefs,
        "redactionLevel": redactionLevel,
        if (requestedBy != null) "requestedBy": requestedBy,
        "correlationId": correlationId,
      };
}

class NodeSnapshotHostHealth {
  final List<NodeSnapshotHostHealthDisks> disks;
  final NodeSnapshotHostHealthThermal thermal;
  final NodeSnapshotHostHealthBackups? backups;
  const NodeSnapshotHostHealth({required this.disks, required this.thermal, this.backups});
  factory NodeSnapshotHostHealth.fromJson(Map<String, dynamic> json) => NodeSnapshotHostHealth(
        disks: (json["disks"] as List).map((e0) => NodeSnapshotHostHealthDisks.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
        thermal: NodeSnapshotHostHealthThermal.fromJson(Map<String, dynamic>.from(json["thermal"] as Map)),
        backups: json["backups"] == null ? null : NodeSnapshotHostHealthBackups.fromJson(Map<String, dynamic>.from(json["backups"] as Map)),
      );
  Map<String, dynamic> toJson() => {
        "disks": disks.map((e0) => e0.toJson()).toList(),
        "thermal": thermal.toJson(),
        if (backups != null) "backups": backups!.toJson(),
      };
}

class NodeSnapshotHostHealthDisks {
  final String path;
  final int? freeBytes;
  final int? totalBytes;
  final double? freePercent;
  final String? error;
  const NodeSnapshotHostHealthDisks({required this.path, this.freeBytes, this.totalBytes, this.freePercent, this.error});
  factory NodeSnapshotHostHealthDisks.fromJson(Map<String, dynamic> json) => NodeSnapshotHostHealthDisks(
        path: json["path"] as String,
        freeBytes: json["freeBytes"] == null ? null : (json["freeBytes"] as num).toInt(),
        totalBytes: json["totalBytes"] == null ? null : (json["totalBytes"] as num).toInt(),
        freePercent: json["freePercent"] == null ? null : (json["freePercent"] as num).toDouble(),
        error: json["error"] == null ? null : json["error"] as String,
      );
  Map<String, dynamic> toJson() => {
        "path": path,
        if (freeBytes != null) "freeBytes": freeBytes,
        if (totalBytes != null) "totalBytes": totalBytes,
        if (freePercent != null) "freePercent": freePercent,
        if (error != null) "error": error,
      };
}

class NodeSnapshotHostHealthThermal {
  final double? celsius;
  final int? throttledRaw;
  final List<String> throttledNow;
  final List<String> throttledPast;
  final bool vcgencmdAvailable;
  const NodeSnapshotHostHealthThermal({this.celsius, this.throttledRaw, required this.throttledNow, required this.throttledPast, required this.vcgencmdAvailable});
  factory NodeSnapshotHostHealthThermal.fromJson(Map<String, dynamic> json) => NodeSnapshotHostHealthThermal(
        celsius: json["celsius"] == null ? null : (json["celsius"] as num).toDouble(),
        throttledRaw: json["throttledRaw"] == null ? null : (json["throttledRaw"] as num).toInt(),
        throttledNow: (json["throttledNow"] as List).map((e0) => e0 as String).toList(),
        throttledPast: (json["throttledPast"] as List).map((e0) => e0 as String).toList(),
        vcgencmdAvailable: json["vcgencmdAvailable"] as bool,
      );
  Map<String, dynamic> toJson() => {
        if (celsius != null) "celsius": celsius,
        if (throttledRaw != null) "throttledRaw": throttledRaw,
        "throttledNow": throttledNow,
        "throttledPast": throttledPast,
        "vcgencmdAvailable": vcgencmdAvailable,
      };
}

class NodeSnapshotHostHealthBackups {
  final String directory;
  final int? count;
  final double? newestAgeDays;
  final String? error;
  const NodeSnapshotHostHealthBackups({required this.directory, this.count, this.newestAgeDays, this.error});
  factory NodeSnapshotHostHealthBackups.fromJson(Map<String, dynamic> json) => NodeSnapshotHostHealthBackups(
        directory: json["directory"] as String,
        count: json["count"] == null ? null : (json["count"] as num).toInt(),
        newestAgeDays: json["newestAgeDays"] == null ? null : (json["newestAgeDays"] as num).toDouble(),
        error: json["error"] == null ? null : json["error"] as String,
      );
  Map<String, dynamic> toJson() => {
        "directory": directory,
        if (count != null) "count": count,
        if (newestAgeDays != null) "newestAgeDays": newestAgeDays,
        if (error != null) "error": error,
      };
}

class Operation {
  final String schema_version;
  final String operation_id;
  final String correlation_id;
  final String kind;
  final OperationTarget target;
  final String status;
  final String? status_reason;
  final String requested_at_utc;
  final String updated_at_utc;
  final Map<String, Object?> params;
  final OperationError? error;
  final OperationResult? result;
  const Operation({required this.schema_version, required this.operation_id, required this.correlation_id, required this.kind, required this.target, required this.status, this.status_reason, required this.requested_at_utc, required this.updated_at_utc, required this.params, this.error, this.result});
  factory Operation.fromJson(Map<String, dynamic> json) => Operation(
        schema_version: json["schema_version"] as String,
        operation_id: json["operation_id"] as String,
        correlation_id: json["correlation_id"] as String,
        kind: json["kind"] as String,
        target: OperationTarget.fromJson(Map<String, dynamic>.from(json["target"] as Map)),
        status: json["status"] as String,
        status_reason: json["status_reason"] == null ? null : json["status_reason"] as String,
        requested_at_utc: json["requested_at_utc"] as String,
        updated_at_utc: json["updated_at_utc"] as String,
        params: Map<String, dynamic>.from(json["params"] as Map),
        error: json["error"] == null ? null : OperationError.fromJson(Map<String, dynamic>.from(json["error"] as Map)),
        result: json["result"] == null ? null : OperationResult.fromJson(Map<String, dynamic>.from(json["result"] as Map)),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "operation_id": operation_id,
        "correlation_id": correlation_id,
        "kind": kind,
        "target": target.toJson(),
        "status": status,
        if (status_reason != null) "status_reason": status_reason,
        "requested_at_utc": requested_at_utc,
        "updated_at_utc": updated_at_utc,
        "params": params,
        if (error != null) "error": error!.toJson(),
        if (result != null) "result": result!.toJson(),
      };
}

class OperationTarget {
  final String kind;
  final String id;
  const OperationTarget({required this.kind, required this.id});
  factory OperationTarget.fromJson(Map<String, dynamic> json) => OperationTarget(
        kind: json["kind"] as String,
        id: json["id"] as String,
      );
  Map<String, dynamic> toJson() => {
        "kind": kind,
        "id": id,
      };
}

class OperationError {
  final String code;
  final String message;
  const OperationError({required this.code, required this.message});
  factory OperationError.fromJson(Map<String, dynamic> json) => OperationError(
        code: json["code"] as String,
        message: json["message"] as String,
      );
  Map<String, dynamic> toJson() => {
        "code": code,
        "message": message,
      };
}

class OperationResult {
  final String run_id;
  final String? revision;
  final String origin;
  final bool observers_enabled;
  final String? accepted_at_utc;
  final String? executed_at_utc;
  final String? observed_at_utc;
  final String outcome;
  final String? outcome_reason;
  const OperationResult({required this.run_id, this.revision, required this.origin, required this.observers_enabled, this.accepted_at_utc, this.executed_at_utc, this.observed_at_utc, required this.outcome, this.outcome_reason});
  factory OperationResult.fromJson(Map<String, dynamic> json) => OperationResult(
        run_id: json["run_id"] as String,
        revision: json["revision"] == null ? null : json["revision"] as String,
        origin: json["origin"] as String,
        observers_enabled: json["observers_enabled"] as bool,
        accepted_at_utc: json["accepted_at_utc"] == null ? null : json["accepted_at_utc"] as String,
        executed_at_utc: json["executed_at_utc"] == null ? null : json["executed_at_utc"] as String,
        observed_at_utc: json["observed_at_utc"] == null ? null : json["observed_at_utc"] as String,
        outcome: json["outcome"] as String,
        outcome_reason: json["outcome_reason"] == null ? null : json["outcome_reason"] as String,
      );
  Map<String, dynamic> toJson() => {
        "run_id": run_id,
        if (revision != null) "revision": revision,
        "origin": origin,
        "observers_enabled": observers_enabled,
        if (accepted_at_utc != null) "accepted_at_utc": accepted_at_utc,
        if (executed_at_utc != null) "executed_at_utc": executed_at_utc,
        if (observed_at_utc != null) "observed_at_utc": observed_at_utc,
        "outcome": outcome,
        if (outcome_reason != null) "outcome_reason": outcome_reason,
      };
}

class Pose {
  final String schema_version;
  final String frame;
  final PosePosition position;
  final PoseOrientation orientation;
  final PoseEuler? euler;
  const Pose({required this.schema_version, required this.frame, required this.position, required this.orientation, this.euler});
  factory Pose.fromJson(Map<String, dynamic> json) => Pose(
        schema_version: json["schema_version"] as String,
        frame: json["frame"] as String,
        position: PosePosition.fromJson(Map<String, dynamic>.from(json["position"] as Map)),
        orientation: PoseOrientation.fromJson(Map<String, dynamic>.from(json["orientation"] as Map)),
        euler: json["euler"] == null ? null : PoseEuler.fromJson(Map<String, dynamic>.from(json["euler"] as Map)),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "frame": frame,
        "position": position.toJson(),
        "orientation": orientation.toJson(),
        if (euler != null) "euler": euler!.toJson(),
      };
}

class PosePosition {
  final double x;
  final double y;
  final double z;
  const PosePosition({required this.x, required this.y, required this.z});
  factory PosePosition.fromJson(Map<String, dynamic> json) => PosePosition(
        x: (json["x"] as num).toDouble(),
        y: (json["y"] as num).toDouble(),
        z: (json["z"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "x": x,
        "y": y,
        "z": z,
      };
}

class PoseOrientation {
  final double w;
  final double x;
  final double y;
  final double z;
  const PoseOrientation({required this.w, required this.x, required this.y, required this.z});
  factory PoseOrientation.fromJson(Map<String, dynamic> json) => PoseOrientation(
        w: (json["w"] as num).toDouble(),
        x: (json["x"] as num).toDouble(),
        y: (json["y"] as num).toDouble(),
        z: (json["z"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "w": w,
        "x": x,
        "y": y,
        "z": z,
      };
}

class PoseEuler {
  final double roll;
  final double pitch;
  final double yaw;
  const PoseEuler({required this.roll, required this.pitch, required this.yaw});
  factory PoseEuler.fromJson(Map<String, dynamic> json) => PoseEuler(
        roll: (json["roll"] as num).toDouble(),
        pitch: (json["pitch"] as num).toDouble(),
        yaw: (json["yaw"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
      };
}

class ProductionEvent {
  final String schema_version;
  final String source_id;
  final String at_utc;
  final bool good;
  final double cycle_time_s;
  final String? job_id;
  final String? reject_reason;
  const ProductionEvent({required this.schema_version, required this.source_id, required this.at_utc, required this.good, required this.cycle_time_s, this.job_id, this.reject_reason});
  factory ProductionEvent.fromJson(Map<String, dynamic> json) => ProductionEvent(
        schema_version: json["schema_version"] as String,
        source_id: json["source_id"] as String,
        at_utc: json["at_utc"] as String,
        good: json["good"] as bool,
        cycle_time_s: (json["cycle_time_s"] as num).toDouble(),
        job_id: json["job_id"] == null ? null : json["job_id"] as String,
        reject_reason: json["reject_reason"] == null ? null : json["reject_reason"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "source_id": source_id,
        "at_utc": at_utc,
        "good": good,
        "cycle_time_s": cycle_time_s,
        if (job_id != null) "job_id": job_id,
        if (reject_reason != null) "reject_reason": reject_reason,
      };
}

class ProjectManifest {
  final String schema_version;
  final String ecosystem;
  final String name;
  final String version;
  final String role;
  final String stack;
  final List<String> technologies;
  final String deployment_target;
  final String maturity;
  final String? evidence;
  final bool? hardware_bound;
  final List<String>? depends_on;
  final String? deployment_target_note;
  final ProjectManifestService? service;
  final String family;
  final String? parent;
  final ProjectManifestNativeVersion native_version;
  final String build;
  final String notes;
  const ProjectManifest({required this.schema_version, required this.ecosystem, required this.name, required this.version, required this.role, required this.stack, required this.technologies, required this.deployment_target, required this.maturity, this.evidence, this.hardware_bound, this.depends_on, this.deployment_target_note, this.service, required this.family, this.parent, required this.native_version, required this.build, required this.notes});
  factory ProjectManifest.fromJson(Map<String, dynamic> json) => ProjectManifest(
        schema_version: json["schema_version"] as String,
        ecosystem: json["ecosystem"] as String,
        name: json["name"] as String,
        version: json["version"] as String,
        role: json["role"] as String,
        stack: json["stack"] as String,
        technologies: (json["technologies"] as List).map((e0) => e0 as String).toList(),
        deployment_target: json["deployment_target"] as String,
        maturity: json["maturity"] as String,
        evidence: json["evidence"] == null ? null : json["evidence"] as String,
        hardware_bound: json["hardware_bound"] == null ? null : json["hardware_bound"] as bool,
        depends_on: json["depends_on"] == null ? null : (json["depends_on"] as List).map((e0) => e0 as String).toList(),
        deployment_target_note: json["deployment_target_note"] == null ? null : json["deployment_target_note"] as String,
        service: json["service"] == null ? null : ProjectManifestService.fromJson(Map<String, dynamic>.from(json["service"] as Map)),
        family: json["family"] as String,
        parent: json["parent"] == null ? null : json["parent"] as String,
        native_version: ProjectManifestNativeVersion.fromJson(Map<String, dynamic>.from(json["native_version"] as Map)),
        build: json["build"] as String,
        notes: json["notes"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "ecosystem": ecosystem,
        "name": name,
        "version": version,
        "role": role,
        "stack": stack,
        "technologies": technologies,
        "deployment_target": deployment_target,
        "maturity": maturity,
        if (evidence != null) "evidence": evidence,
        if (hardware_bound != null) "hardware_bound": hardware_bound,
        if (depends_on != null) "depends_on": depends_on,
        if (deployment_target_note != null) "deployment_target_note": deployment_target_note,
        if (service != null) "service": service!.toJson(),
        "family": family,
        if (parent != null) "parent": parent,
        "native_version": native_version.toJson(),
        "build": build,
        "notes": notes,
      };
}

class ProjectManifestService {
  final int? port;
  final String? health_path;
  final String? systemd_unit;
  final int? grpc_port;
  final String? grpc_service;
  const ProjectManifestService({this.port, this.health_path, this.systemd_unit, this.grpc_port, this.grpc_service});
  factory ProjectManifestService.fromJson(Map<String, dynamic> json) => ProjectManifestService(
        port: json["port"] == null ? null : (json["port"] as num).toInt(),
        health_path: json["health_path"] == null ? null : json["health_path"] as String,
        systemd_unit: json["systemd_unit"] == null ? null : json["systemd_unit"] as String,
        grpc_port: json["grpc_port"] == null ? null : (json["grpc_port"] as num).toInt(),
        grpc_service: json["grpc_service"] == null ? null : json["grpc_service"] as String,
      );
  Map<String, dynamic> toJson() => {
        if (port != null) "port": port,
        if (health_path != null) "health_path": health_path,
        if (systemd_unit != null) "systemd_unit": systemd_unit,
        if (grpc_port != null) "grpc_port": grpc_port,
        if (grpc_service != null) "grpc_service": grpc_service,
      };
}

class ProjectManifestNativeVersion {
  final String file;
  final Object? pattern;
  const ProjectManifestNativeVersion({required this.file, this.pattern});
  factory ProjectManifestNativeVersion.fromJson(Map<String, dynamic> json) => ProjectManifestNativeVersion(
        file: json["file"] as String,
        pattern: json["pattern"],
      );
  Map<String, dynamic> toJson() => {
        "file": file,
        "pattern": pattern,
      };
}

class RobotLiveness {
  final String schema_version;
  final int stale_after_s;
  final List<RobotLivenessRobots> robots;
  const RobotLiveness({required this.schema_version, required this.stale_after_s, required this.robots});
  factory RobotLiveness.fromJson(Map<String, dynamic> json) => RobotLiveness(
        schema_version: json["schema_version"] as String,
        stale_after_s: (json["stale_after_s"] as num).toInt(),
        robots: (json["robots"] as List).map((e0) => RobotLivenessRobots.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "stale_after_s": stale_after_s,
        "robots": robots.map((e0) => e0.toJson()).toList(),
      };
}

class RobotLivenessRobots {
  final String controller_id;
  final int robot_id;
  final String state;
  final String? last_update_utc;
  final int? age_s;
  final String? source;
  const RobotLivenessRobots({required this.controller_id, required this.robot_id, required this.state, this.last_update_utc, this.age_s, this.source});
  factory RobotLivenessRobots.fromJson(Map<String, dynamic> json) => RobotLivenessRobots(
        controller_id: json["controller_id"] as String,
        robot_id: (json["robot_id"] as num).toInt(),
        state: json["state"] as String,
        last_update_utc: json["last_update_utc"] == null ? null : json["last_update_utc"] as String,
        age_s: json["age_s"] == null ? null : (json["age_s"] as num).toInt(),
        source: json["source"] == null ? null : json["source"] as String,
      );
  Map<String, dynamic> toJson() => {
        "controller_id": controller_id,
        "robot_id": robot_id,
        "state": state,
        if (last_update_utc != null) "last_update_utc": last_update_utc,
        if (age_s != null) "age_s": age_s,
        if (source != null) "source": source,
      };
}

class RobotState {
  final String schema_version;
  final String robot_id;
  final String state;
  final String? source;
  final String updated_at_utc;
  final String? mission_id;
  final double? battery_percent;
  final RobotStatePose? pose;
  const RobotState({required this.schema_version, required this.robot_id, required this.state, this.source, required this.updated_at_utc, this.mission_id, this.battery_percent, this.pose});
  factory RobotState.fromJson(Map<String, dynamic> json) => RobotState(
        schema_version: json["schema_version"] as String,
        robot_id: json["robot_id"] as String,
        state: json["state"] as String,
        source: json["source"] == null ? null : json["source"] as String,
        updated_at_utc: json["updated_at_utc"] as String,
        mission_id: json["mission_id"] == null ? null : json["mission_id"] as String,
        battery_percent: json["battery_percent"] == null ? null : (json["battery_percent"] as num).toDouble(),
        pose: json["pose"] == null ? null : RobotStatePose.fromJson(Map<String, dynamic>.from(json["pose"] as Map)),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "robot_id": robot_id,
        "state": state,
        if (source != null) "source": source,
        "updated_at_utc": updated_at_utc,
        if (mission_id != null) "mission_id": mission_id,
        if (battery_percent != null) "battery_percent": battery_percent,
        if (pose != null) "pose": pose!.toJson(),
      };
}

class RobotStatePose {
  final String schema_version;
  final String frame;
  final RobotStatePosePosition position;
  final RobotStatePoseOrientation orientation;
  const RobotStatePose({required this.schema_version, required this.frame, required this.position, required this.orientation});
  factory RobotStatePose.fromJson(Map<String, dynamic> json) => RobotStatePose(
        schema_version: json["schema_version"] as String,
        frame: json["frame"] as String,
        position: RobotStatePosePosition.fromJson(Map<String, dynamic>.from(json["position"] as Map)),
        orientation: RobotStatePoseOrientation.fromJson(Map<String, dynamic>.from(json["orientation"] as Map)),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "frame": frame,
        "position": position.toJson(),
        "orientation": orientation.toJson(),
      };
}

class RobotStatePosePosition {
  final double x;
  final double y;
  final double z;
  const RobotStatePosePosition({required this.x, required this.y, required this.z});
  factory RobotStatePosePosition.fromJson(Map<String, dynamic> json) => RobotStatePosePosition(
        x: (json["x"] as num).toDouble(),
        y: (json["y"] as num).toDouble(),
        z: (json["z"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "x": x,
        "y": y,
        "z": z,
      };
}

class RobotStatePoseOrientation {
  final double w;
  final double x;
  final double y;
  final double z;
  const RobotStatePoseOrientation({required this.w, required this.x, required this.y, required this.z});
  factory RobotStatePoseOrientation.fromJson(Map<String, dynamic> json) => RobotStatePoseOrientation(
        w: (json["w"] as num).toDouble(),
        x: (json["x"] as num).toDouble(),
        y: (json["y"] as num).toDouble(),
        z: (json["z"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "w": w,
        "x": x,
        "y": y,
        "z": z,
      };
}

class SafetyState {
  final String schema_version;
  final String state;
  final String source;
  final String timestamp_utc;
  const SafetyState({required this.schema_version, required this.state, required this.source, required this.timestamp_utc});
  factory SafetyState.fromJson(Map<String, dynamic> json) => SafetyState(
        schema_version: json["schema_version"] as String,
        state: json["state"] as String,
        source: json["source"] as String,
        timestamp_utc: json["timestamp_utc"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "state": state,
        "source": source,
        "timestamp_utc": timestamp_utc,
      };
}

class ScenarioOutcome {
  final String schema_version;
  final String scenario_id;
  final String run_id;
  final String base_fingerprint;
  final String phase;
  final String repro_case;
  final ScenarioOutcomeObserved observed;
  final String timestamp_utc;
  const ScenarioOutcome({required this.schema_version, required this.scenario_id, required this.run_id, required this.base_fingerprint, required this.phase, required this.repro_case, required this.observed, required this.timestamp_utc});
  factory ScenarioOutcome.fromJson(Map<String, dynamic> json) => ScenarioOutcome(
        schema_version: json["schema_version"] as String,
        scenario_id: json["scenario_id"] as String,
        run_id: json["run_id"] as String,
        base_fingerprint: json["base_fingerprint"] as String,
        phase: json["phase"] as String,
        repro_case: json["repro_case"] as String,
        observed: ScenarioOutcomeObserved.fromJson(Map<String, dynamic>.from(json["observed"] as Map)),
        timestamp_utc: json["timestamp_utc"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "scenario_id": scenario_id,
        "run_id": run_id,
        "base_fingerprint": base_fingerprint,
        "phase": phase,
        "repro_case": repro_case,
        "observed": observed.toJson(),
        "timestamp_utc": timestamp_utc,
      };
}

class ScenarioOutcomeObserved {
  final String outcome;
  final int? exit_code;
  final String? evidence;
  const ScenarioOutcomeObserved({required this.outcome, this.exit_code, this.evidence});
  factory ScenarioOutcomeObserved.fromJson(Map<String, dynamic> json) => ScenarioOutcomeObserved(
        outcome: json["outcome"] as String,
        exit_code: json["exit_code"] == null ? null : (json["exit_code"] as num).toInt(),
        evidence: json["evidence"] == null ? null : json["evidence"] as String,
      );
  Map<String, dynamic> toJson() => {
        "outcome": outcome,
        if (exit_code != null) "exit_code": exit_code,
        if (evidence != null) "evidence": evidence,
      };
}

class ServerDiscovery {
  final String schema_version;
  final String product;
  final int remoteApiVersion;
  final String appVersion;
  final String hostname;
  final int controllerCount;
  final int robotCount;
  final int uptimeSeconds;
  const ServerDiscovery({required this.schema_version, required this.product, required this.remoteApiVersion, required this.appVersion, required this.hostname, required this.controllerCount, required this.robotCount, required this.uptimeSeconds});
  factory ServerDiscovery.fromJson(Map<String, dynamic> json) => ServerDiscovery(
        schema_version: json["schema_version"] as String,
        product: json["product"] as String,
        remoteApiVersion: (json["remoteApiVersion"] as num).toInt(),
        appVersion: json["appVersion"] as String,
        hostname: json["hostname"] as String,
        controllerCount: (json["controllerCount"] as num).toInt(),
        robotCount: (json["robotCount"] as num).toInt(),
        uptimeSeconds: (json["uptimeSeconds"] as num).toInt(),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "product": product,
        "remoteApiVersion": remoteApiVersion,
        "appVersion": appVersion,
        "hostname": hostname,
        "controllerCount": controllerCount,
        "robotCount": robotCount,
        "uptimeSeconds": uptimeSeconds,
      };
}

class ToolDescriptor {
  final String schema_version;
  final int tool_id;
  final String name;
  final String title;
  final String kind;
  final String? category;
  final ToolDescriptorHeroMetric? hero_metric;
  final ToolDescriptorLimits? limits;
  final int? watchdog_ms;
  final List<String>? features;
  final String? expansion_board;
  final String? min_firmware_version;
  const ToolDescriptor({required this.schema_version, required this.tool_id, required this.name, required this.title, required this.kind, this.category, this.hero_metric, this.limits, this.watchdog_ms, this.features, this.expansion_board, this.min_firmware_version});
  factory ToolDescriptor.fromJson(Map<String, dynamic> json) => ToolDescriptor(
        schema_version: json["schema_version"] as String,
        tool_id: (json["tool_id"] as num).toInt(),
        name: json["name"] as String,
        title: json["title"] as String,
        kind: json["kind"] as String,
        category: json["category"] == null ? null : json["category"] as String,
        hero_metric: json["hero_metric"] == null ? null : ToolDescriptorHeroMetric.fromJson(Map<String, dynamic>.from(json["hero_metric"] as Map)),
        limits: json["limits"] == null ? null : ToolDescriptorLimits.fromJson(Map<String, dynamic>.from(json["limits"] as Map)),
        watchdog_ms: json["watchdog_ms"] == null ? null : (json["watchdog_ms"] as num).toInt(),
        features: json["features"] == null ? null : (json["features"] as List).map((e0) => e0 as String).toList(),
        expansion_board: json["expansion_board"] == null ? null : json["expansion_board"] as String,
        min_firmware_version: json["min_firmware_version"] == null ? null : json["min_firmware_version"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "tool_id": tool_id,
        "name": name,
        "title": title,
        "kind": kind,
        if (category != null) "category": category,
        if (hero_metric != null) "hero_metric": hero_metric!.toJson(),
        if (limits != null) "limits": limits!.toJson(),
        if (watchdog_ms != null) "watchdog_ms": watchdog_ms,
        if (features != null) "features": features,
        if (expansion_board != null) "expansion_board": expansion_board,
        if (min_firmware_version != null) "min_firmware_version": min_firmware_version,
      };
}

class ToolDescriptorHeroMetric {
  final String label;
  final String unit;
  const ToolDescriptorHeroMetric({required this.label, required this.unit});
  factory ToolDescriptorHeroMetric.fromJson(Map<String, dynamic> json) => ToolDescriptorHeroMetric(
        label: json["label"] as String,
        unit: json["unit"] as String,
      );
  Map<String, dynamic> toJson() => {
        "label": label,
        "unit": unit,
      };
}

class ToolDescriptorLimits {
  final double default_;
  final double min;
  final double max;
  const ToolDescriptorLimits({required this.default_, required this.min, required this.max});
  factory ToolDescriptorLimits.fromJson(Map<String, dynamic> json) => ToolDescriptorLimits(
        default_: (json["default"] as num).toDouble(),
        min: (json["min"] as num).toDouble(),
        max: (json["max"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "default": default_,
        "min": min,
        "max": max,
      };
}

class ToolState {
  final String schema_version;
  final int tool_id;
  final String state;
  final String source;
  final String timestamp_utc;
  final String? firmware_version;
  final ToolStateCan? can;
  final double? temperature_c;
  final double? setpoint_c;
  final double? mcu_temp_c;
  final int? vdda_mv;
  final bool? critical_error;
  final String? thermal_fault;
  const ToolState({required this.schema_version, required this.tool_id, required this.state, required this.source, required this.timestamp_utc, this.firmware_version, this.can, this.temperature_c, this.setpoint_c, this.mcu_temp_c, this.vdda_mv, this.critical_error, this.thermal_fault});
  factory ToolState.fromJson(Map<String, dynamic> json) => ToolState(
        schema_version: json["schema_version"] as String,
        tool_id: (json["tool_id"] as num).toInt(),
        state: json["state"] as String,
        source: json["source"] as String,
        timestamp_utc: json["timestamp_utc"] as String,
        firmware_version: json["firmware_version"] == null ? null : json["firmware_version"] as String,
        can: json["can"] == null ? null : ToolStateCan.fromJson(Map<String, dynamic>.from(json["can"] as Map)),
        temperature_c: json["temperature_c"] == null ? null : (json["temperature_c"] as num).toDouble(),
        setpoint_c: json["setpoint_c"] == null ? null : (json["setpoint_c"] as num).toDouble(),
        mcu_temp_c: json["mcu_temp_c"] == null ? null : (json["mcu_temp_c"] as num).toDouble(),
        vdda_mv: json["vdda_mv"] == null ? null : (json["vdda_mv"] as num).toInt(),
        critical_error: json["critical_error"] == null ? null : json["critical_error"] as bool,
        thermal_fault: json["thermal_fault"] == null ? null : json["thermal_fault"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "tool_id": tool_id,
        "state": state,
        "source": source,
        "timestamp_utc": timestamp_utc,
        if (firmware_version != null) "firmware_version": firmware_version,
        if (can != null) "can": can!.toJson(),
        if (temperature_c != null) "temperature_c": temperature_c,
        if (setpoint_c != null) "setpoint_c": setpoint_c,
        if (mcu_temp_c != null) "mcu_temp_c": mcu_temp_c,
        if (vdda_mv != null) "vdda_mv": vdda_mv,
        if (critical_error != null) "critical_error": critical_error,
        if (thermal_fault != null) "thermal_fault": thermal_fault,
      };
}

class ToolStateCan {
  final String state;
  final int? tec;
  final int? rec;
  final int? bus_off_count;
  const ToolStateCan({required this.state, this.tec, this.rec, this.bus_off_count});
  factory ToolStateCan.fromJson(Map<String, dynamic> json) => ToolStateCan(
        state: json["state"] as String,
        tec: json["tec"] == null ? null : (json["tec"] as num).toInt(),
        rec: json["rec"] == null ? null : (json["rec"] as num).toInt(),
        bus_off_count: json["bus_off_count"] == null ? null : (json["bus_off_count"] as num).toInt(),
      );
  Map<String, dynamic> toJson() => {
        "state": state,
        if (tec != null) "tec": tec,
        if (rec != null) "rec": rec,
        if (bus_off_count != null) "bus_off_count": bus_off_count,
      };
}

class TwinState {
  final String schema_version;
  final String source;
  final String? robot_id;
  final String frame;
  final String timestamp_utc;
  final int? sequence;
  final List<TwinStateJointStates> joint_states;
  final List<TwinStatePoses>? poses;
  const TwinState({required this.schema_version, required this.source, this.robot_id, required this.frame, required this.timestamp_utc, this.sequence, required this.joint_states, this.poses});
  factory TwinState.fromJson(Map<String, dynamic> json) => TwinState(
        schema_version: json["schema_version"] as String,
        source: json["source"] as String,
        robot_id: json["robot_id"] == null ? null : json["robot_id"] as String,
        frame: json["frame"] as String,
        timestamp_utc: json["timestamp_utc"] as String,
        sequence: json["sequence"] == null ? null : (json["sequence"] as num).toInt(),
        joint_states: (json["joint_states"] as List).map((e0) => TwinStateJointStates.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
        poses: json["poses"] == null ? null : (json["poses"] as List).map((e0) => TwinStatePoses.fromJson(Map<String, dynamic>.from(e0 as Map))).toList(),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "source": source,
        if (robot_id != null) "robot_id": robot_id,
        "frame": frame,
        "timestamp_utc": timestamp_utc,
        if (sequence != null) "sequence": sequence,
        "joint_states": joint_states.map((e0) => e0.toJson()).toList(),
        if (poses != null) "poses": poses!.map((e0) => e0.toJson()).toList(),
      };
}

class TwinStateJointStates {
  final String name;
  final double position;
  final double? velocity;
  final double? effort;
  const TwinStateJointStates({required this.name, required this.position, this.velocity, this.effort});
  factory TwinStateJointStates.fromJson(Map<String, dynamic> json) => TwinStateJointStates(
        name: json["name"] as String,
        position: (json["position"] as num).toDouble(),
        velocity: json["velocity"] == null ? null : (json["velocity"] as num).toDouble(),
        effort: json["effort"] == null ? null : (json["effort"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "name": name,
        "position": position,
        if (velocity != null) "velocity": velocity,
        if (effort != null) "effort": effort,
      };
}

class TwinStatePoses {
  final String name;
  final TwinStatePosesPose pose;
  const TwinStatePoses({required this.name, required this.pose});
  factory TwinStatePoses.fromJson(Map<String, dynamic> json) => TwinStatePoses(
        name: json["name"] as String,
        pose: TwinStatePosesPose.fromJson(Map<String, dynamic>.from(json["pose"] as Map)),
      );
  Map<String, dynamic> toJson() => {
        "name": name,
        "pose": pose.toJson(),
      };
}

class TwinStatePosesPose {
  final String schema_version;
  final String frame;
  final TwinStatePosesPosePosition position;
  final TwinStatePosesPoseOrientation orientation;
  const TwinStatePosesPose({required this.schema_version, required this.frame, required this.position, required this.orientation});
  factory TwinStatePosesPose.fromJson(Map<String, dynamic> json) => TwinStatePosesPose(
        schema_version: json["schema_version"] as String,
        frame: json["frame"] as String,
        position: TwinStatePosesPosePosition.fromJson(Map<String, dynamic>.from(json["position"] as Map)),
        orientation: TwinStatePosesPoseOrientation.fromJson(Map<String, dynamic>.from(json["orientation"] as Map)),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "frame": frame,
        "position": position.toJson(),
        "orientation": orientation.toJson(),
      };
}

class TwinStatePosesPosePosition {
  final double x;
  final double y;
  final double z;
  const TwinStatePosesPosePosition({required this.x, required this.y, required this.z});
  factory TwinStatePosesPosePosition.fromJson(Map<String, dynamic> json) => TwinStatePosesPosePosition(
        x: (json["x"] as num).toDouble(),
        y: (json["y"] as num).toDouble(),
        z: (json["z"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "x": x,
        "y": y,
        "z": z,
      };
}

class TwinStatePosesPoseOrientation {
  final double w;
  final double x;
  final double y;
  final double z;
  const TwinStatePosesPoseOrientation({required this.w, required this.x, required this.y, required this.z});
  factory TwinStatePosesPoseOrientation.fromJson(Map<String, dynamic> json) => TwinStatePosesPoseOrientation(
        w: (json["w"] as num).toDouble(),
        x: (json["x"] as num).toDouble(),
        y: (json["y"] as num).toDouble(),
        z: (json["z"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "w": w,
        "x": x,
        "y": y,
        "z": z,
      };
}

class UpdateManifest {
  final String schema_version;
  final String project;
  final String version;
  final String artifact_url;
  final String sha256;
  final String? signature;
  final String? signature_alg;
  final String? key_id;
  final String? min_bootloader;
  final String? target;
  const UpdateManifest({required this.schema_version, required this.project, required this.version, required this.artifact_url, required this.sha256, this.signature, this.signature_alg, this.key_id, this.min_bootloader, this.target});
  factory UpdateManifest.fromJson(Map<String, dynamic> json) => UpdateManifest(
        schema_version: json["schema_version"] as String,
        project: json["project"] as String,
        version: json["version"] as String,
        artifact_url: json["artifact_url"] as String,
        sha256: json["sha256"] as String,
        signature: json["signature"] == null ? null : json["signature"] as String,
        signature_alg: json["signature_alg"] == null ? null : json["signature_alg"] as String,
        key_id: json["key_id"] == null ? null : json["key_id"] as String,
        min_bootloader: json["min_bootloader"] == null ? null : json["min_bootloader"] as String,
        target: json["target"] == null ? null : json["target"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "project": project,
        "version": version,
        "artifact_url": artifact_url,
        "sha256": sha256,
        if (signature != null) "signature": signature,
        if (signature_alg != null) "signature_alg": signature_alg,
        if (key_id != null) "key_id": key_id,
        if (min_bootloader != null) "min_bootloader": min_bootloader,
        if (target != null) "target": target,
      };
}

class VelocityCommand {
  final String schema_version;
  final double vx;
  final double vy;
  final double vz;
  final double wroll;
  final double wpitch;
  final double wyaw;
  final bool hold;
  final int issued_at_ms;
  final double valid_for_ms;
  final int seq;
  final String? frame_id;
  const VelocityCommand({required this.schema_version, required this.vx, required this.vy, required this.vz, required this.wroll, required this.wpitch, required this.wyaw, required this.hold, required this.issued_at_ms, required this.valid_for_ms, required this.seq, this.frame_id});
  factory VelocityCommand.fromJson(Map<String, dynamic> json) => VelocityCommand(
        schema_version: json["schema_version"] as String,
        vx: (json["vx"] as num).toDouble(),
        vy: (json["vy"] as num).toDouble(),
        vz: (json["vz"] as num).toDouble(),
        wroll: (json["wroll"] as num).toDouble(),
        wpitch: (json["wpitch"] as num).toDouble(),
        wyaw: (json["wyaw"] as num).toDouble(),
        hold: json["hold"] as bool,
        issued_at_ms: (json["issued_at_ms"] as num).toInt(),
        valid_for_ms: (json["valid_for_ms"] as num).toDouble(),
        seq: (json["seq"] as num).toInt(),
        frame_id: json["frame_id"] == null ? null : json["frame_id"] as String,
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "vx": vx,
        "vy": vy,
        "vz": vz,
        "wroll": wroll,
        "wpitch": wpitch,
        "wyaw": wyaw,
        "hold": hold,
        "issued_at_ms": issued_at_ms,
        "valid_for_ms": valid_for_ms,
        "seq": seq,
        if (frame_id != null) "frame_id": frame_id,
      };
}

class VisualTargetRequest {
  final String schema_version;
  final String frame_id;
  final VisualTargetRequestCurrent current;
  final VisualTargetRequestTarget target;
  final double confidence;
  final String safety_state;
  final double? data_age_ms;
  final String? captured_at_utc;
  final String? calibration_version;
  final double? calibration_age_days;
  const VisualTargetRequest({required this.schema_version, required this.frame_id, required this.current, required this.target, required this.confidence, required this.safety_state, this.data_age_ms, this.captured_at_utc, this.calibration_version, this.calibration_age_days});
  factory VisualTargetRequest.fromJson(Map<String, dynamic> json) => VisualTargetRequest(
        schema_version: json["schema_version"] as String,
        frame_id: json["frame_id"] as String,
        current: VisualTargetRequestCurrent.fromJson(Map<String, dynamic>.from(json["current"] as Map)),
        target: VisualTargetRequestTarget.fromJson(Map<String, dynamic>.from(json["target"] as Map)),
        confidence: (json["confidence"] as num).toDouble(),
        safety_state: json["safety_state"] as String,
        data_age_ms: json["data_age_ms"] == null ? null : (json["data_age_ms"] as num).toDouble(),
        captured_at_utc: json["captured_at_utc"] == null ? null : json["captured_at_utc"] as String,
        calibration_version: json["calibration_version"] == null ? null : json["calibration_version"] as String,
        calibration_age_days: json["calibration_age_days"] == null ? null : (json["calibration_age_days"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "schema_version": schema_version,
        "frame_id": frame_id,
        "current": current.toJson(),
        "target": target.toJson(),
        "confidence": confidence,
        "safety_state": safety_state,
        if (data_age_ms != null) "data_age_ms": data_age_ms,
        if (captured_at_utc != null) "captured_at_utc": captured_at_utc,
        if (calibration_version != null) "calibration_version": calibration_version,
        if (calibration_age_days != null) "calibration_age_days": calibration_age_days,
      };
}

class VisualTargetRequestCurrent {
  final double x;
  final double y;
  final double z;
  final double roll;
  final double pitch;
  final double yaw;
  const VisualTargetRequestCurrent({required this.x, required this.y, required this.z, required this.roll, required this.pitch, required this.yaw});
  factory VisualTargetRequestCurrent.fromJson(Map<String, dynamic> json) => VisualTargetRequestCurrent(
        x: (json["x"] as num).toDouble(),
        y: (json["y"] as num).toDouble(),
        z: (json["z"] as num).toDouble(),
        roll: (json["roll"] as num).toDouble(),
        pitch: (json["pitch"] as num).toDouble(),
        yaw: (json["yaw"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "x": x,
        "y": y,
        "z": z,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
      };
}

class VisualTargetRequestTarget {
  final double x;
  final double y;
  final double z;
  final double roll;
  final double pitch;
  final double yaw;
  const VisualTargetRequestTarget({required this.x, required this.y, required this.z, required this.roll, required this.pitch, required this.yaw});
  factory VisualTargetRequestTarget.fromJson(Map<String, dynamic> json) => VisualTargetRequestTarget(
        x: (json["x"] as num).toDouble(),
        y: (json["y"] as num).toDouble(),
        z: (json["z"] as num).toDouble(),
        roll: (json["roll"] as num).toDouble(),
        pitch: (json["pitch"] as num).toDouble(),
        yaw: (json["yaw"] as num).toDouble(),
      );
  Map<String, dynamic> toJson() => {
        "x": x,
        "y": y,
        "z": z,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
      };
}
