/*
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

const { expect } = require('chai');
const { Context } = require('fabric-contract-api');
const { ChaincodeStub, ClientIdentity } = require('fabric-shim');
const sinon = require('sinon');

const VendorContract = require('../lib/vendorContract.js');

describe('VendorContract', () => {
  let contract;
  let ctx;
  let stub;
  let clientIdentity;

  beforeEach(() => {
    contract = new VendorContract();
    ctx = sinon.createStubInstance(Context);
    stub = sinon.createStubInstance(ChaincodeStub);
    clientIdentity = sinon.createStubInstance(ClientIdentity);
    ctx.stub = stub;
    ctx.clientIdentity = clientIdentity;
  });

  describe('#initLedger', () => {
    it('should initialize the ledger with sample contracts', async () => {
      const putStateStub = stub.putState;
      putStateStub.returns(Promise.resolve());

      await contract.initLedger(ctx);

      expect(putStateStub.calledOnce).to.be.true;
      const call = putStateStub.getCall(0);
      expect(call.args[0]).to.equal('CONTRACT0');
      
      const contractData = JSON.parse(call.args[1].toString());
      expect(contractData.contractId).to.equal('CONTRACT001');
      expect(contractData.docType).to.equal('contract');
      expect(contractData.status).to.equal('SUBMITTED');
    });
  });

  describe('#createContract', () => {
    it('should create a new contract in CREATED status', async () => {
      const putStateStub = stub.putState;
      putStateStub.returns(Promise.resolve());
      clientIdentity.getID.returns('testUser@org1.vendorchain.com');

      const contractId = 'CONTRACT002';
      const vendorId = 'VENDOR002';
      const vendorName = 'Test Vendor';
      const contractType = 'Service Agreement';
      const expiryDate = '2025-12-31';
      const totalValue = '75000';

      const result = await contract.createContract(
        ctx,
        contractId,
        vendorId,
        vendorName,
        contractType,
        expiryDate,
        totalValue
      );

      expect(putStateStub.calledOnce).to.be.true;
      const call = putStateStub.getCall(0);
      expect(call.args[0]).to.equal(contractId);

      const contractData = JSON.parse(call.args[1].toString());
      expect(contractData.contractId).to.equal(contractId);
      expect(contractData.vendorId).to.equal(vendorId);
      expect(contractData.vendorName).to.equal(vendorName);
      expect(contractData.contractType).to.equal(contractType);
      expect(contractData.status).to.equal('CREATED');
      expect(contractData.totalValue).to.equal(75000);
      expect(contractData.paidAmount).to.equal(0);
      expect(contractData.remainingAmount).to.equal(75000);
      expect(contractData.createdBy).to.equal('testUser@org1.vendorchain.com');
      expect(contractData.verifiedBy).to.equal('');
      expect(contractData.submittedAt).to.equal('');

      const resultData = JSON.parse(result);
      expect(resultData.status).to.equal('CREATED');
    });

    it('should validate required fields for contract creation', async () => {
      const putStateStub = stub.putState;
      putStateStub.returns(Promise.resolve());
      clientIdentity.getID.returns('testUser@org1.vendorchain.com');

      // Test with missing vendor name
      try {
        await contract.createContract(
          ctx,
          'CONTRACT003',
          'VENDOR003',
          '', // empty vendor name
          'Service Agreement',
          '2025-12-31',
          '50000'
        );
        expect.fail('Should have thrown error for empty vendor name');
      } catch (error) {
        expect(error.message).to.include('Vendor name is required');
      }
    });
  });

  describe('#verifyContract', () => {
    it('should verify a contract in CREATED status', async () => {
      const contractId = 'CONTRACT002';
      const existingContract = {
        contractId: contractId,
        docType: 'contract',
        vendorId: 'VENDOR002',
        vendorName: 'Test Vendor',
        contractType: 'Service Agreement',
        status: 'CREATED',
        createdBy: 'creator@org1.vendorchain.com',
        createdAt: '2025-08-19T10:00:00.000Z',
        verifiedBy: '',
        verifiedAt: '',
        submittedAt: '',
        expiryDate: '2025-12-31',
        totalValue: 75000,
        paidAmount: 0,
        remainingAmount: 75000,
        paymentHistory: [],
        documents: []
      };

      stub.getState.withArgs(contractId).returns(Promise.resolve(Buffer.from(JSON.stringify(existingContract))));
      const putStateStub = stub.putState;
      putStateStub.returns(Promise.resolve());
      clientIdentity.getID.returns('verificator@org1.vendorchain.com');

      const result = await contract.verifyContract(ctx, contractId);

      expect(putStateStub.calledOnce).to.be.true;
      const call = putStateStub.getCall(0);
      expect(call.args[0]).to.equal(contractId);

      const updatedContract = JSON.parse(call.args[1].toString());
      expect(updatedContract.status).to.equal('VERIFIED');
      expect(updatedContract.verifiedBy).to.equal('verificator@org1.vendorchain.com');
      expect(updatedContract.verifiedAt).to.not.be.empty;

      const resultData = JSON.parse(result);
      expect(resultData.status).to.equal('VERIFIED');
    });

    it('should throw error when verifying non-existent contract', async () => {
      const contractId = 'NONEXISTENT';
      stub.getState.withArgs(contractId).returns(Promise.resolve(Buffer.from('')));
      clientIdentity.getID.returns('verificator@org1.vendorchain.com');

      try {
        await contract.verifyContract(ctx, contractId);
        expect.fail('Should have thrown error for non-existent contract');
      } catch (error) {
        expect(error.message).to.equal(`Contract ${contractId} does not exist`);
      }
    });

    it('should throw error when verifying contract not in CREATED status', async () => {
      const contractId = 'CONTRACT002';
      const existingContract = {
        contractId: contractId,
        status: 'VERIFIED' // Already verified
      };

      stub.getState.withArgs(contractId).returns(Promise.resolve(Buffer.from(JSON.stringify(existingContract))));
      clientIdentity.getID.returns('verificator@org1.vendorchain.com');

      try {
        await contract.verifyContract(ctx, contractId);
        expect.fail('Should have thrown error for contract not in CREATED status');
      } catch (error) {
        expect(error.message).to.include('is not in CREATED status');
      }
    });
  });

  describe('#submitContract', () => {
    it('should submit a contract in VERIFIED status', async () => {
      const contractId = 'CONTRACT002';
      const existingContract = {
        contractId: contractId,
        docType: 'contract',
        vendorId: 'VENDOR002',
        vendorName: 'Test Vendor',
        contractType: 'Service Agreement',
        status: 'VERIFIED',
        createdBy: 'creator@org1.vendorchain.com',
        createdAt: '2025-08-19T10:00:00.000Z',
        verifiedBy: 'verifier@org1.vendorchain.com',
        verifiedAt: '2025-08-19T11:00:00.000Z',
        submittedAt: '',
        expiryDate: '2025-12-31',
        totalValue: 75000,
        paidAmount: 0,
        remainingAmount: 75000,
        paymentHistory: [],
        documents: []
      };

      stub.getState.withArgs(contractId).returns(Promise.resolve(Buffer.from(JSON.stringify(existingContract))));
      const putStateStub = stub.putState;
      putStateStub.returns(Promise.resolve());
      clientIdentity.getID.returns('admin@org1.vendorchain.com');

      const result = await contract.submitContract(ctx, contractId);

      expect(putStateStub.calledOnce).to.be.true;
      const call = putStateStub.getCall(0);
      expect(call.args[0]).to.equal(contractId);

      const updatedContract = JSON.parse(call.args[1].toString());
      expect(updatedContract.status).to.equal('SUBMITTED');
      expect(updatedContract.submittedAt).to.not.be.empty;

      const resultData = JSON.parse(result);
      expect(resultData.status).to.equal('SUBMITTED');
    });

    it('should throw error when submitting non-existent contract', async () => {
      const contractId = 'NONEXISTENT';
      stub.getState.withArgs(contractId).returns(Promise.resolve(Buffer.from('')));
      clientIdentity.getID.returns('admin@org1.vendorchain.com');

      try {
        await contract.submitContract(ctx, contractId);
        expect.fail('Should have thrown error for non-existent contract');
      } catch (error) {
        expect(error.message).to.equal(`Contract ${contractId} does not exist`);
      }
    });

    it('should throw error when submitting contract not in VERIFIED status', async () => {
      const contractId = 'CONTRACT002';
      const existingContract = {
        contractId: contractId,
        status: 'CREATED', // Not yet verified
        expiryDate: '2025-12-31'
      };

      stub.getState.withArgs(contractId).returns(Promise.resolve(Buffer.from(JSON.stringify(existingContract))));
      clientIdentity.getID.returns('admin@org1.vendorchain.com');

      try {
        await contract.submitContract(ctx, contractId);
        expect.fail('Should have thrown error for contract not in VERIFIED status');
      } catch (error) {
        expect(error.message).to.include('is not in VERIFIED status');
      }
    });
  });

  describe('#queryContract', () => {
    it('should return contract data when contract exists', async () => {
      const contractId = 'CONTRACT002';
      const existingContract = {
        contractId: contractId,
        docType: 'contract',
        vendorId: 'VENDOR002',
        vendorName: 'Test Vendor',
        status: 'CREATED'
      };

      stub.getState.withArgs(contractId).returns(Promise.resolve(Buffer.from(JSON.stringify(existingContract))));

      const result = await contract.queryContract(ctx, contractId);

      const resultData = JSON.parse(result);
      expect(resultData.contractId).to.equal(contractId);
      expect(resultData.vendorId).to.equal('VENDOR002');
      expect(resultData.status).to.equal('CREATED');
    });

    it('should throw error when querying non-existent contract', async () => {
      const contractId = 'NONEXISTENT';
      stub.getState.withArgs(contractId).returns(Promise.resolve(Buffer.from('')));

      try {
        await contract.queryContract(ctx, contractId);
        expect.fail('Should have thrown error for non-existent contract');
      } catch (error) {
        expect(error.message).to.equal(`Contract ${contractId} does not exist`);
      }
    });
  });

  describe('#recordPayment', () => {
    it('should record payment for contract in SUBMITTED status', async () => {
      const contractId = 'CONTRACT002';
      const existingContract = {
        contractId: contractId,
        docType: 'contract',
        status: 'SUBMITTED',
        totalValue: 75000,
        paidAmount: 0,
        remainingAmount: 75000,
        paymentHistory: []
      };

      stub.getState.withArgs(contractId).returns(Promise.resolve(Buffer.from(JSON.stringify(existingContract))));
      const putStateStub = stub.putState;
      putStateStub.returns(Promise.resolve());
      clientIdentity.getID.returns('admin@org1.vendorchain.com');

      const paymentAmount = '25000';
      const paymentDate = '2025-08-19';
      const paymentReference = 'PAY001';

      const result = await contract.recordPayment(ctx, contractId, paymentAmount, paymentDate, paymentReference);

      expect(putStateStub.calledOnce).to.be.true;
      const call = putStateStub.getCall(0);
      expect(call.args[0]).to.equal(contractId);

      const updatedContract = JSON.parse(call.args[1].toString());
      expect(updatedContract.paidAmount).to.equal(25000);
      expect(updatedContract.remainingAmount).to.equal(50000);
      expect(updatedContract.paymentHistory).to.have.length(1);
      expect(updatedContract.paymentHistory[0].amount).to.equal(25000);
      expect(updatedContract.paymentHistory[0].reference).to.equal(paymentReference);
      expect(updatedContract.paymentHistory[0].recordedBy).to.equal('admin@org1.vendorchain.com');

      const resultData = JSON.parse(result);
      expect(resultData.paidAmount).to.equal(25000);
    });

    it('should throw error when recording payment for contract not in SUBMITTED status', async () => {
      const contractId = 'CONTRACT002';
      const existingContract = {
        contractId: contractId,
        status: 'VERIFIED' // Not yet submitted
      };

      stub.getState.withArgs(contractId).returns(Promise.resolve(Buffer.from(JSON.stringify(existingContract))));
      clientIdentity.getID.returns('admin@org1.vendorchain.com');

      try {
        await contract.recordPayment(ctx, contractId, '25000', '2025-08-19', 'PAY001');
        expect.fail('Should have thrown error for contract not in SUBMITTED status');
      } catch (error) {
        expect(error.message).to.include('is not in SUBMITTED status');
      }
    });
  });

  describe('#queryAllContracts', () => {
    it('should return all contracts', async () => {
      const contract1 = { contractId: 'CONTRACT001', status: 'SUBMITTED' };
      const contract2 = { contractId: 'CONTRACT002', status: 'CREATED' };

      const mockIterator = [
        { key: 'CONTRACT001', value: Buffer.from(JSON.stringify(contract1)) },
        { key: 'CONTRACT002', value: Buffer.from(JSON.stringify(contract2)) }
      ];

      stub.getStateByRange.returns(mockIterator);

      const result = await contract.queryAllContracts(ctx);

      const resultData = JSON.parse(result);
      expect(resultData).to.have.length(2);
      expect(resultData[0].Key).to.equal('CONTRACT001');
      expect(resultData[0].Record.contractId).to.equal('CONTRACT001');
      expect(resultData[1].Key).to.equal('CONTRACT002');
      expect(resultData[1].Record.contractId).to.equal('CONTRACT002');
    });
  });

  describe('#getContractsByVendor', () => {
    it('should return contracts for specific vendor', async () => {
      const vendorId = 'VENDOR002';
      const contract1 = { contractId: 'CONTRACT002', vendorId: vendorId, status: 'CREATED' };
      const contract2 = { contractId: 'CONTRACT003', vendorId: vendorId, status: 'VERIFIED' };

      const mockIterator = {
        next: sinon.stub()
      };

      mockIterator.next
        .onFirstCall().returns(Promise.resolve({
          value: { key: 'CONTRACT002', value: Buffer.from(JSON.stringify(contract1)) },
          done: false
        }))
        .onSecondCall().returns(Promise.resolve({
          value: { key: 'CONTRACT003', value: Buffer.from(JSON.stringify(contract2)) },
          done: false
        }))
        .onThirdCall().returns(Promise.resolve({ done: true }));

      mockIterator.close = sinon.stub().returns(Promise.resolve());

      stub.getQueryResult.returns(Promise.resolve(mockIterator));

      const result = await contract.getContractsByVendor(ctx, vendorId);

      const resultData = JSON.parse(result);
      expect(resultData).to.have.length(2);
      expect(resultData[0].Record.vendorId).to.equal(vendorId);
      expect(resultData[1].Record.vendorId).to.equal(vendorId);
    });
  });

  describe('#getExpiringContracts', () => {
    it('should return contracts expiring within specified days', async () => {
      const daysAhead = '30';
      const contract1 = { 
        contractId: 'CONTRACT002', 
        status: 'SUBMITTED',
        expiryDate: '2025-09-15'
      };

      const mockIterator = {
        next: sinon.stub()
      };

      mockIterator.next
        .onFirstCall().returns(Promise.resolve({
          value: { key: 'CONTRACT002', value: Buffer.from(JSON.stringify(contract1)) },
          done: false
        }))
        .onSecondCall().returns(Promise.resolve({ done: true }));

      mockIterator.close = sinon.stub().returns(Promise.resolve());

      stub.getQueryResult.returns(Promise.resolve(mockIterator));

      const result = await contract.getExpiringContracts(ctx, daysAhead);

      const resultData = JSON.parse(result);
      expect(resultData).to.have.length(1);
      expect(resultData[0].Record.contractId).to.equal('CONTRACT002');
      expect(resultData[0].Record.status).to.equal('SUBMITTED');
    });
  });

  describe('#getContractHistory', () => {
    it('should return contract transaction history', async () => {
      const contractId = 'CONTRACT002';
      
      const mockIterator = {
        next: sinon.stub()
      };

      const historyEntry1 = {
        txId: 'tx001',
        timestamp: { seconds: { low: 1692441600 } },
        isDelete: false,
        value: Buffer.from(JSON.stringify({ contractId: contractId, status: 'CREATED' }))
      };

      const historyEntry2 = {
        txId: 'tx002',
        timestamp: { seconds: { low: 1692445200 } },
        isDelete: false,
        value: Buffer.from(JSON.stringify({ contractId: contractId, status: 'VERIFIED' }))
      };

      mockIterator.next
        .onFirstCall().returns(Promise.resolve({
          value: historyEntry1,
          done: false
        }))
        .onSecondCall().returns(Promise.resolve({
          value: historyEntry2,
          done: false
        }))
        .onThirdCall().returns(Promise.resolve({ done: true }));

      mockIterator.close = sinon.stub().returns(Promise.resolve());

      stub.getHistoryForKey.withArgs(contractId).returns(Promise.resolve(mockIterator));

      const result = await contract.getContractHistory(ctx, contractId);

      const resultData = JSON.parse(result);
      expect(resultData).to.have.length(2);
      expect(resultData[0].TxId).to.equal('tx001');
      expect(resultData[0].Value.status).to.equal('CREATED');
      expect(resultData[1].TxId).to.equal('tx002');
      expect(resultData[1].Value.status).to.equal('VERIFIED');
    });
  });
});