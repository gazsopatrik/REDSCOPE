import axios from 'axios';
import { Project, Scope, Target, Scan, Finding, Validation, AuditLog } from '../types';

const api = axios.create({
  baseURL: '/api',
});

export const getProjects = async (): Promise<Project[]> => (await api.get('/projects')).data;
export const getProject = async (id: string): Promise<Project> => (await api.get(`/projects/${id}`)).data;
export const createProject = async (data: Partial<Project>): Promise<Project> => (await api.post('/projects', data)).data;
export const updateProject = async (id: string, data: Partial<Project>): Promise<Project> => (await api.patch(`/projects/${id}`, data)).data;

export const getScopes = async (projectId: string): Promise<Scope[]> => (await api.get(`/projects/${projectId}/scopes`)).data;
export const createScope = async (projectId: string, data: Partial<Scope>): Promise<Scope> => (await api.post(`/projects/${projectId}/scopes`, data)).data;
export const deleteScope = async (scopeId: string): Promise<void> => await api.delete(`/scopes/${scopeId}`);

export const getAllTargets = async (): Promise<Target[]> => (await api.get('/targets')).data;
export const getTargets = async (projectId: string): Promise<Target[]> => (await api.get(`/projects/${projectId}/targets`)).data;
export const createTarget = async (projectId: string, data: Partial<Target>): Promise<Target> => (await api.post(`/projects/${projectId}/targets`, data)).data;
export const validateTargetScope = async (targetId: string): Promise<Target> => (await api.post(`/targets/${targetId}/validate-scope`)).data;

export const getScans = async (projectId: string): Promise<Scan[]> => (await api.get(`/projects/${projectId}/scans`)).data;
export const createScan = async (projectId: string, data: { target_id: string; profile: string; custom_ports?: string }): Promise<Scan> => (await api.post(`/projects/${projectId}/scans`, data)).data;

export const getFindings = async (projectId: string): Promise<Finding[]> => (await api.get(`/projects/${projectId}/findings`)).data;

export const getAuditLogs = async (projectId: string): Promise<AuditLog[]> => (await api.get(`/projects/${projectId}/audit-logs`)).data;
