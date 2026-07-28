import axios from 'axios';
import { Project, Scope, Target, Scan, Finding, Validation, AuditLog } from '../types';

const api = axios.create({
  baseURL: '/api',
});

export const getProjects = async (): Promise<Project[]> => (await api.get('/projects')).data;
export const createProject = async (data: Partial<Project>): Promise<Project> => (await api.post('/projects', data)).data;

export const getScopes = async (projectId: string): Promise<Scope[]> => (await api.get(`/projects/${projectId}/scopes`)).data;
export const createScope = async (projectId: string, data: Partial<Scope>): Promise<Scope> => (await api.post(`/projects/${projectId}/scopes`, data)).data;

export const getTargets = async (projectId: string): Promise<Target[]> => (await api.get(`/projects/${projectId}/targets`)).data;
export const createTarget = async (projectId: string, data: Partial<Target>): Promise<Target> => (await api.post(`/projects/${projectId}/targets`, data)).data;

export const getScans = async (projectId: string): Promise<Scan[]> => (await api.get(`/projects/${projectId}/scans`)).data;
export const createScan = async (projectId: string, data: { target_id: string; profile: string }): Promise<Scan> => (await api.post(`/projects/${projectId}/scans`, data)).data;

export const getFindings = async (projectId: string): Promise<Finding[]> => (await api.get(`/projects/${projectId}/findings`)).data;

export const getAuditLogs = async (projectId: string): Promise<AuditLog[]> => (await api.get(`/projects/${projectId}/audit-logs`)).data;
